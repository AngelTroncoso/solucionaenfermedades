#!/usr/bin/env python3
"""
Pharma Loop Engineering - Main Entry Point
Orchestrates pharmaceutical discovery workflows using AI agents.

Usage:
    python main.py --start          Start the loop engineering cycle
    python main.py --pause          Pause the running loop
    python main.py --resume         Resume a paused loop
    python main.py --status         Show system status
    python main.py --export         Export final reports
    python main.py --dashboard      Launch Streamlit dashboard
"""

import sys
import os
import signal
import time
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml
from loguru import logger

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.orchestrator import OrchestratorAgent
from agents.researcher import ResearcherAgent
from agents.designer import DesignAgent as DesignerAgent
from agents.implementer import ImplementerAgent
from agents.evaluator import EvaluatorAgent
from agents.refiner import RefinerAgent
from worktrees.state_manager import WorktreeManager
from config.settings import load_config, load_prompts, get_log_level

# Global reference for graceful shutdown
_loop_engine = None


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging with loguru."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    logger.add(
        "logs/pharma_loop.log",
        rotation="10 MB",
        retention="1 month",
        compression="zip",
        level=log_level
    )
    logger.add(
        "logs/pharma_loop_error.log",
        rotation="50 MB",
        retention="1 week",
        level="ERROR"
    )
    logger.info(f"Logging configured at {log_level} level")


def load_configuration() -> dict:
    """Load configuration from YAML files."""
    config_path = project_root / "config" / "settings.yaml"
    prompts_path = project_root / "config" / "prompts.yaml"

    config = load_config(str(config_path))

    prompts = load_prompts(str(prompts_path))
    if prompts:
        config["prompts"] = prompts

    return config


def load_ideas_from_json(path: str = None) -> List[Dict[str, Any]]:
    """Load pharmaceutical ideas from JSON file or use defaults."""
    if path and Path(path).exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data.get('ideas', []))} ideas from {path}")
            return data.get('ideas', [])
        except Exception as e:
            logger.error(f"Failed to load ideas from {path}: {e}")

    # Fallback: use sample ideas from orchestrator
    logger.info("Using default sample ideas")
    return OrchestratorAgent.SAMPLE_IDEAS_JSON.get('ideas', [])


def initialize_system(config: dict) -> tuple:
    """
    Initialize all system components.

    Returns:
        Tuple of (OrchestratorAgent, WorktreeManager, dict of agents)
    """
    logger.info("=" * 60)
    logger.info("  Initializing Pharma Loop Engineering System")
    logger.info("=" * 60)

    # Initialize WorktreeManager
    worktree_manager = WorktreeManager(config.get('storage', {}))
    logger.info("WorktreeManager initialized")

    # Initialize plugins
    plugins = initialize_plugins(config)

    # Initialize agents
    agents_config = config.get("agents", {})

    researcher = ResearcherAgent({
        **agents_config.get("researcher", {}),
        'pubmed_plugin': plugins.get('pubmed'),
        'chembl_plugin': plugins.get('chembl'),
        'llm_plugin': plugins.get('llm')
    })
    logger.info("ResearcherAgent initialized")

    designer = DesignerAgent({
        **agents_config.get("designer", {}),
        'llm_plugin': plugins.get('llm')
    })
    logger.info("DesignerAgent initialized")

    implementer = ImplementerAgent({
        **agents_config.get("implementer", {}),
        'llm_plugin': plugins.get('llm')
    })
    logger.info("ImplementerAgent initialized")

    evaluator = EvaluatorAgent({
        **agents_config.get("evaluator", {}),
        'llm_plugin': plugins.get('llm')
    })
    logger.info("EvaluatorAgent initialized")

    refiner = RefinerAgent({
        **agents_config.get("refiner", {}),
        'llm_plugin': plugins.get('llm')
    })
    logger.info("RefinerAgent initialized")

    # Initialize orchestrator
    orchestrator = OrchestratorAgent(config.get("orchestrator", {}))
    orchestrator.register_agent("researcher", researcher)
    orchestrator.register_agent("designer", designer)
    orchestrator.register_agent("implementer", implementer)
    orchestrator.register_agent("evaluator", evaluator)
    orchestrator.register_agent("refiner", refiner)
    logger.info("All agents registered in orchestrator")

    logger.info("=" * 60)
    logger.info("  System initialization complete")
    logger.info(f"  Registered agents: {list(orchestrator.agents.keys())}")
    logger.info("=" * 60)

    return orchestrator, worktree_manager, {
        'researcher': researcher,
        'designer': designer,
        'implementer': implementer,
        'evaluator': evaluator,
        'refiner': refiner
    }


def initialize_plugins(config: dict) -> Dict[str, Any]:
    """Initialize plugins from configuration."""
    plugins = {}

    # LLM Plugin
    try:
        from plugins.llm_plugin import LLMPlugin
        plugins['llm'] = LLMPlugin(config.get('plugins', {}).get('llm', {}))
        logger.info("LLMPlugin loaded")
    except Exception as e:
        logger.warning(f"LLMPlugin not available: {e}")
        plugins['llm'] = None

    # PubMed Plugin
    try:
        from plugins.pubmed_plugin import PubMedPlugin
        plugins['pubmed'] = PubMedPlugin(config.get('plugins', {}).get('pubmed', {}))
        logger.info("PubMedPlugin loaded")
    except Exception as e:
        logger.warning(f"PubMedPlugin not available: {e}")
        plugins['pubmed'] = None

    # ChEMBL Plugin
    try:
        from plugins.chembl_plugin import ChEMBLPlugin
        plugins['chembl'] = ChEMBLPlugin(config.get('plugins', {}).get('chembl', {}))
        logger.info("ChEMBLPlugin loaded")
    except Exception as e:
        logger.warning(f"ChEMBLPlugin not available: {e}")
        plugins['chembl'] = None

    # Visualization Plugin
    try:
        from plugins.visualization_plugin import VisualizationPlugin
        plugins['visualization'] = VisualizationPlugin(config.get('plugins', {}).get('visualization', {}))
        logger.info("VisualizationPlugin loaded")
    except Exception as e:
        logger.warning(f"VisualizationPlugin not available: {e}")
        plugins['visualization'] = None

    return plugins


class LoopEngine:
    """
    Main Loop Engineering engine.
    Coordinates the complete drug repositioning pipeline across all worktrees.
    """

    def __init__(self, config: dict, orchestrator: OrchestratorAgent,
                 worktree_manager: WorktreeManager, agents: dict):
        self.config = config
        self.orchestrator = orchestrator
        self.worktree_manager = worktree_manager
        self.agents = agents
        self._running = False
        self._shutdown_requested = False

        self.loop_interval = config.get('loop_interval', 1)
        self.max_iterations = config.get('max_iterations', 5)
        self.dashboard_callback = config.get('dashboard_callback')

        logger.info("LoopEngine initialized")

    async def process_worktree(self, worktree: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single worktree through the full pipeline.

        Pipeline:
        1. Researcher (investigation)
        2. Designer (design)
        3. Implementer (implementation)
        4. Evaluator (evaluation)
        5. Refiner (refinement)
        6. Loop back or complete

        Args:
            worktree: Worktree state dictionary

        Returns:
            Updated worktree with results
        """
        worktree_id = worktree['id']
        drug = worktree.get('drug_name', 'Unknown')
        disease = worktree.get('target_disease', 'Unknown')

        logger.info(f"Processing worktree {worktree_id}: {drug} -> {disease}")

        # Mark as processing
        self.worktree_manager.update_status(worktree_id, 'procesando')

        try:
            # === Phase 1: Research ===
            logger.info(f"[{worktree_id}] Phase 1: Research")
            self.worktree_manager.update_phase(worktree_id, 'investigacion')

            research_result = self.agents['researcher'].research(worktree)
            self.worktree_manager.save_results(worktree_id, {
                'investigacion': research_result,
                'relevance_score': research_result.get('summary', {}).get('relevance_score', 0)
            })

            if self._shutdown_requested:
                return self.worktree_manager.get_worktree(worktree_id)

            # === Phase 2: Design ===
            logger.info(f"[{worktree_id}] Phase 2: Design")
            self.worktree_manager.update_phase(worktree_id, 'diseno')

            design_result = self.agents['designer'].design(research_result)
            self.worktree_manager.save_results(worktree_id, {
                'diseno': design_result
            })

            if self._shutdown_requested:
                return self.worktree_manager.get_worktree(worktree_id)

            # === Phase 3: Implementation ===
            logger.info(f"[{worktree_id}] Phase 3: Implementation")
            self.worktree_manager.update_phase(worktree_id, 'implementacion')

            implementation_result = self.agents['implementer'].implement(design_result)
            self.worktree_manager.save_results(worktree_id, {
                'implementacion': implementation_result
            })

            if self._shutdown_requested:
                return self.worktree_manager.get_worktree(worktree_id)

            # === Phase 4: Evaluation ===
            logger.info(f"[{worktree_id}] Phase 4: Evaluation")
            self.worktree_manager.update_phase(worktree_id, 'evaluacion')

            evaluation_result = self.agents['evaluator'].evaluate(implementation_result)
            self.worktree_manager.save_results(worktree_id, {
                'evaluacion': evaluation_result,
                'confidence_score': evaluation_result.get('confidence_score', 0)
            })

            if self._shutdown_requested:
                return self.worktree_manager.get_worktree(worktree_id)

            # === Phase 5: Refinement ===
            logger.info(f"[{worktree_id}] Phase 5: Refinement")
            self.worktree_manager.update_phase(worktree_id, 'refinamiento')

            refinement_result = self.agents['refiner'].refine(evaluation_result)
            self.worktree_manager.save_results(worktree_id, {
                'refinamiento': refinement_result
            })

            # === Decision: Complete or loop back ===
            binary_rec = evaluation_result.get('binary_recommendation', 'refine')
            confidence = evaluation_result.get('confidence_score', 0)

            if binary_rec == 'proceed' or confidence >= 75:
                # Mark as completed
                self.worktree_manager.update_status(worktree_id, 'completado')
                self.worktree_manager.update_phase(worktree_id, 'completado')

                # Add to discoveries
                self.worktree_manager.save_results(worktree_id, {
                    'discovery_date': time.time(),
                    'is_discovery': True
                })

                logger.success(f"[{worktree_id}] COMPLETED (confidence: {confidence})")

            elif binary_rec == 'abort' or refinement_result.get('status') == 'completed':
                # Mark as completed (refiner says it's done)
                self.worktree_manager.update_status(worktree_id, 'completado')
                self.worktree_manager.update_phase(worktree_id, 'completado')
                logger.success(f"[{worktree_id}] COMPLETED after refinement")

            else:
                # REFINE: loop back for another iteration
                iterations = self.worktree_manager.get_worktree(worktree_id).get('iterations', 0)
                if iterations < self.max_iterations:
                    self.worktree_manager.update_status(worktree_id, 'pendiente')
                    logger.info(f"[{worktree_id}] Scheduling refinement iteration {iterations + 1}/{self.max_iterations}")
                else:
                    self.worktree_manager.update_status(worktree_id, 'completado')
                    self.worktree_manager.update_phase(worktree_id, 'completado')
                    logger.info(f"[{worktree_id}] COMPLETED (max iterations reached)")

            # Update dashboard
            self._update_dashboard(worktree_id)

        except Exception as e:
            logger.error(f"[{worktree_id}] Processing failed: {e}")
            self.worktree_manager.log_error(worktree_id, str(e))
            self.worktree_manager.update_status(worktree_id, 'error')

            # Auto-retry logic
            retry_count = self.worktree_manager.get_worktree(worktree_id).get('retry_count', 0)
            if retry_count < self.worktree_manager.max_retries:
                logger.info(f"[{worktree_id}] Scheduling retry {retry_count + 1}/{self.worktree_manager.max_retries}")
                self.worktree_manager.update_status(worktree_id, 'pendiente')

        return self.worktree_manager.get_worktree(worktree_id)

    def _update_dashboard(self, worktree_id: str) -> None:
        """Update dashboard with latest progress."""
        if self.dashboard_callback:
            try:
                worktree = self.worktree_manager.get_worktree(worktree_id)
                self.dashboard_callback({
                    'type': 'worktree_update',
                    'worktree_id': worktree_id,
                    'data': {
                        'status': worktree.get('status'),
                        'phase': worktree.get('phase'),
                        'confidence_score': worktree.get('confidence_score', 0),
                        'relevance_score': worktree.get('relevance_score', 0),
                        'iterations': worktree.get('iterations', 0)
                    }
                })
            except Exception as e:
                logger.warning(f"Dashboard update failed: {e}")

    async def run_cycle(self) -> None:
        """Main loop engineering cycle."""
        self._running = True
        logger.info("Starting main loop engineering cycle")

        while self._running and not self._shutdown_requested:
            # Get next pending worktree
            pending = self.worktree_manager.get_pending_worktrees()

            if not pending:
                # Check if any worktrees are still processing
                active = self.worktree_manager.get_active_worktrees()
                failed = self.worktree_manager.get_failed_worktrees()

                if not active and not failed:
                    logger.success("All worktrees processed. Cycle complete.")
                    self.generate_final_report()
                else:
                    logger.info(f"Waiting: {len(active)} active, {len(failed)} failed worktrees")

                self._running = False
                break

            # Process next worktree
            worktree = pending[0]
            await self.process_worktree(worktree)

            # Brief pause between worktrees
            await asyncio.sleep(self.loop_interval)

        self._running = False
        logger.info("Main loop engineering cycle ended")

    def start(self) -> None:
        """Start the loop engineering cycle."""
        logger.info("Starting Loop Engine...")

        # Load ideas into worktree manager
        ideas_path = self.config.get('ideas_path')
        if ideas_path and Path(ideas_path).exists():
            ideas = load_ideas_from_json(ideas_path)
        else:
            ideas = load_ideas_from_json()

        existing = len(self.worktree_manager.worktrees)
        if existing == 0:
            for idea in ideas:
                self.worktree_manager.create_worktree(
                    drug=idea.get('drug_candidate', idea.get('name', 'Unknown')),
                    disease=idea.get('target_disease', 'Unknown'),
                    priority=idea.get('priority', 'media'),
                    metadata=idea
                )
            logger.info(f"Created {len(ideas)} worktrees from ideas")
        else:
            logger.info(f"Resuming with {existing} existing worktrees")

        # Run the async cycle
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                task = loop.create_task(self.run_cycle())
            else:
                loop.run_until_complete(self.run_cycle())
        except RuntimeError:
            # No event loop running, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_cycle())

    def pause(self) -> None:
        """Pause the loop engineering cycle."""
        self.orchestrator.pause_loop()
        logger.info("Loop paused")

    def resume(self) -> None:
        """Resume the loop engineering cycle."""
        self.orchestrator.resume_loop()
        logger.info("Loop resumed")

    def stop(self) -> None:
        """Stop the loop engineering cycle gracefully."""
        self._shutdown_requested = True
        self._running = False
        self.orchestrator.stop_loop()
        self.worktree_manager.stop_auto_checkpoint()

        # Save final state
        self.worktree_manager._save_state()
        logger.info("Loop stopped gracefully")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        stats = self.worktree_manager.get_statistics()
        orchestrator_status = self.orchestrator.get_status()

        return {
            'system': {
                'running': self._running,
                'shutdown_requested': self._shutdown_requested,
                'loop_interval': self.loop_interval,
                'max_iterations': self.max_iterations
            },
            'orchestrator': {
                'running': orchestrator_status.get('running'),
                'paused': orchestrator_status.get('paused'),
                'current_idea': orchestrator_status.get('current_idea_id'),
                'registered_agents': orchestrator_status.get('registered_agents')
            },
            'worktrees': stats,
            'top_candidates': [
                {
                    'drug': w.get('drug_name'),
                    'disease': w.get('target_disease'),
                    'confidence': w.get('confidence_score', 0),
                    'relevance': w.get('relevance_score', 0),
                    'iterations': w.get('iterations', 0)
                }
                for w in self.worktree_manager.get_top_candidates(5)
            ]
        }

    def generate_final_report(self) -> str:
        """Generate final report after all worktrees are processed."""
        logger.info("=" * 60)
        logger.info("  Generating Final Report")
        logger.info("=" * 60)

        # Export worktree report
        report_path = self.worktree_manager.export_report('json')
        csv_path = self.worktree_manager.export_report('csv')

        # Generate summary
        stats = self.worktree_manager.get_statistics()
        top_candidates = self.worktree_manager.get_top_candidates(10)

        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              Pharma Loop Engineering - Final Report          ║
╚══════════════════════════════════════════════════════════════╝

📊 Statistics:
  Total Worktrees: {stats['total']}
  Completed: {stats['completed']}
  Failed: {stats['failed']}
  Processing: {stats['processing']}
  Pending: {stats['pending']}
  Interrupted: {stats['interrupted']}
  Success Rate: {stats['success_rate']}%
  Average Confidence: {stats['average_confidence_score']}/100

🏆 Top Candidates:
"""
        for i, c in enumerate(top_candidates, 1):
            summary += f"  {i}. {c.get('drug_name', '?')} -> {c.get('target_disease', '?')} (Score: {c.get('confidence_score', 0):.1f})\n"

        summary += f"""
📁 Exported Files:
  JSON: {report_path}
  CSV: {csv_path}

⏰ Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

        logger.info(summary)

        # Save summary to file
        summary_path = project_root / 'data' / f"final_report_{int(time.time())}.txt"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        logger.success(f"Final report saved to {summary_path}")
        return str(summary_path)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _loop_engine
    logger.warning(f"Received signal {signum}. Initiating graceful shutdown...")

    if _loop_engine:
        print("\n")  # Clear the ^C line
        logger.info("Shutting down loop engine...")
        _loop_engine.stop()
        logger.info("Shutdown complete.")

    sys.exit(0)


def show_overview() -> None:
    """Display system overview."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Pharma Loop Engineering System v1.0             ║
╚══════════════════════════════════════════════════════════════╝

📋 Pipeline:
   Research → Design → Implementation → Evaluation → Refinement → Loop

🏗️  Architecture:
   • Agents: Researcher, Designer, Implementer, Evaluator, Refiner
   • Orchestrator: Coordinates agent pipeline
   • Worktree Manager: State persistence for 70 ideas
   • Dashboard: Real-time Streamlit monitoring

⌨️  Commands:
   --start       Begin the loop engineering cycle
   --pause       Pause the running loop
   --resume      Resume a paused loop
   --status      Show current system status
   --export      Export worktree data (JSON + CSV)
   --dashboard   Launch the Streamlit dashboard
   --ideas PATH  Load custom ideas from JSON file
   --help        Show this help message

📚  Output: results/ and logs/ directories
""")


def setup_argparse() -> argparse.ArgumentParser:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Pharma Loop Engineering - AI-driven drug repositioning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --start
  python main.py --start --ideas data/my_ideas.json
  python main.py --status
  python main.py --pause
  python main.py --dashboard
        """
    )
    parser.add_argument('--start', action='store_true', help='Start the loop engineering cycle')
    parser.add_argument('--pause', action='store_true', help='Pause the running loop')
    parser.add_argument('--resume', action='store_true', help='Resume a paused loop')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--export', action='store_true', help='Export worktree data')
    parser.add_argument('--dashboard', action='store_true', help='Launch Streamlit dashboard')
    parser.add_argument('--ideas', type=str, help='Path to JSON file with pharmaceutical ideas')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    return parser


def main() -> int:
    """Main entry point."""
    global _loop_engine

    parser = setup_argparse()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration
    config = load_configuration()
    config['ideas_path'] = args.ideas

    # If no arguments, show overview
    if not any([args.start, args.pause, args.resume, args.status, args.export, args.dashboard]):
        show_overview()
        return 0

    # Handle dashboard command separately
    if args.dashboard:
        logger.info("Launching Streamlit dashboard...")
        from dashboard.app import main as dashboard_main
        dashboard_main()
        return 0

    # Initialize system
    orchestrator, worktree_manager, agents = initialize_system(config)

    # Create Loop Engine
    _loop_engine = LoopEngine(config, orchestrator, worktree_manager, agents)

    # Handle commands
    if args.status:
        status = _loop_engine.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False, default=str))

    elif args.start:
        logger.info("Starting loop engineering cycle...")
        _loop_engine.start()

    elif args.pause:
        _loop_engine.pause()

    elif args.resume:
        _loop_engine.resume()

    elif args.export:
        json_path = worktree_manager.export_report('json')
        csv_path = worktree_manager.export_report('csv')
        logger.info(f"Exported reports: {json_path}, {csv_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())