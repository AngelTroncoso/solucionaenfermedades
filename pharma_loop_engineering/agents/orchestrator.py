"""Orchestrator agent that coordinates all other specialized agents."""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from loguru import logger
from pathlib import Path


class OrchestratorAgent:
    """Central agent that manages workflow and delegates tasks for pharmaceutical research."""

    SAMPLE_IDEAS_JSON = {
        "ideas": [
            {
                "id": "idea_001",
                "name": "Metformina para tratamiento de cáncer de páncreas",
                "description": "Evaluar la eficacia de metformina como agente antiproliferativo en líneas celulares de cáncer pancreático",
                "target_disease": "Cáncer de páncreas",
                "drug_candidate": "Metformina",
                "mechanism": "Activación de AMPK, inhibición de mTOR",
                "priority": "alta",
                "required_phases": ["investigacion", "diseno", "implementacion", "evaluacion", "refinamiento"]
            },
            {
                "id": "idea_002",
                "name": "Disulfiram para terapia de fibrosis quística",
                "description": "Investigar disulfiram como modulador de la proteína CFTR en pacientes con fibrosis quística",
                "target_disease": "Fibrosis quística",
                "drug_candidate": "Disulfiram",
                "mechanism": "Modulación de canales iónicos",
                "priority": "media",
                "required_phases": ["investigacion", "diseno", "implementacion", "evaluacion"]
            },
            {
                "id": "idea_003",
                "name": "Nitazoxanida para infecciones por virus respiratorio sincicial",
                "description": "Evaluar nitazoxanida como antiviral de amplio espectro contra VRS en modelos animales",
                "target_disease": "Infección por VRS",
                "drug_candidate": "Nitazoxanida",
                "mechanism": "Inhibición de la enzima piruvato:ferredoxin oxidoreductasa",
                "priority": "alta",
                "required_phases": ["investigacion", "diseno", "implementacion", "evaluacion", "refinamiento"]
            },
            {
                "id": "idea_004",
                "name": "Sildenafil para prevención de preeclampsia",
                "description": "Analizar sildenafil como profiláctico para preeclampsia en embarazos de alto riesgo",
                "target_disease": "Preeclampsia",
                "drug_candidate": "Sildenafil",
                "mechanism": "Vasodilatación mediada por NO, mejoramiento de perfusión placentaria",
                "priority": "media",
                "required_phases": ["investigacion", "diseno", "implementacion", "evaluacion"]
            },
            {
                "id": "idea_005",
                "name": "Pentoxifilina para tratamiento de fibrosis hepática",
                "description": "Estudiar pentoxifilina como agente antifibrótico en modelos de cirrosis hepática inducida",
                "target_disease": "Fibrosis hepática",
                "drug_candidate": "Pentoxifilina",
                "mechanism": "Inhibición de TNF-α, reducción de inflamación hepática",
                "priority": "baja",
                "required_phases": ["investigacion", "diseno", "implementacion", "evaluacion", "refinamiento"]
            }
        ]
    }

    def __init__(self, config: Dict[str, Any], ideas_path: Optional[str] = None):
        self.config = config
        self.worktree_states: Dict[str, Dict[str, Any]] = {}
        self.agents: Dict[str, Any] = {}
        self._running = False
        self._paused = False
        self._current_idea_id: Optional[str] = None
        self._main_loop_task: Optional[asyncio.Task] = None
        self._checkpoint_task: Optional[asyncio.Task] = None

        # Configuration
        self.checkpoint_interval = config.get('checkpoint_interval', 300)  # 5 minutes
        self.max_retries = config.get('max_retries', 3)
        self.timeout_per_phase = config.get('timeout_per_phase', 3600)  # 1 hour default
        self.dashboard_callback = config.get('dashboard_callback')

        if ideas_path:
            self.load_ideas(ideas_path)
        else:
            self._init_worktree_states(self.SAMPLE_IDEAS_JSON)

        logger.info("OrchestratorAgent initialized with {} ideas".format(len(self.worktree_states)))

    def _init_worktree_states(self, ideas_data: Dict[str, Any]) -> None:
        """Initialize worktree states from ideas data."""
        for idea in ideas_data.get('ideas', []):
            idea_id = idea.get('id')
            self.worktree_states[idea_id] = {
                'id': idea_id,
                'name': idea.get('name', ''),
                'status': 'pendiente',
                'current_phase': None,
                'results': {},
                'iterations': 0,
                'metadata': idea,
                'error_history': [],
                'start_time': None,
                'last_update': None
            }
            logger.debug(f"Initialized worktree: {idea_id} - {idea.get('name')}")

    def load_ideas(self, path: str) -> None:
        """Load research ideas from a JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._init_worktree_states(data)
            logger.info(f"Loaded {len(self.worktree_states)} ideas from {path}")
        except Exception as e:
            logger.error(f"Failed to load ideas from {path}: {e}")
            raise

    def register_agent(self, name: str, agent: Any) -> None:
        """Register a specialized agent."""
        self.agents[name] = agent
        logger.info(f"Registered agent: {name}")

    def save_ideas(self, path: str) -> None:
        """Save current ideas state to JSON."""
        try:
            data = {'ideas': []}
            for state in self.worktree_states.values():
                data['ideas'].append(state.get('metadata', {}))
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved ideas to {path}")
        except Exception as e:
            logger.error(f"Failed to save ideas: {e}")

    async def _execute_phase(self, idea_id: str, phase: str) -> Dict[str, Any]:
        """Execute a single phase for a given idea with timeout and retries."""
        agent_map = {
            'investigacion': 'researcher',
            'diseno': 'designer',
            'implementacion': 'implementer',
            'evaluacion': 'evaluator',
            'refinamiento': 'refiner'
        }

        agent_name = agent_map.get(phase)
        if not agent_name or agent_name not in self.agents:
            logger.warning(f"No agent registered for phase '{phase}' in idea {idea_id}")
            return {'status': 'skipped', 'reason': f'Agent {agent_name} not available'}

        agent = self.agents[agent_name]
        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            try:
                logger.info(f"Executing {phase} for {idea_id} (attempt {attempt + 1}/{self.max_retries})")
                self.worktree_states[idea_id]['current_phase'] = phase
                self.worktree_states[idea_id]['last_update'] = time.time()

                # Execute agent method (may be sync or async)
                if asyncio.iscoroutinefunction(getattr(agent, phase, None)):
                    result = await asyncio.wait_for(
                        getattr(agent, phase)(self.worktree_states[idea_id]['metadata']),
                        timeout=self.timeout_per_phase
                    )
                else:
                    # Wrap sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(
                            None,
                            getattr(agent, phase),
                            self.worktree_states[idea_id]['metadata']
                        ),
                        timeout=self.timeout_per_phase
                    )

                logger.success(f"Phase {phase} completed successfully for {idea_id}")
                return {'status': 'success', 'data': result}

            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.timeout_per_phase}s"
                logger.warning(f"Phase {phase} timed out for {idea_id}: {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"Phase {phase} failed for {idea_id}: {last_error}")

            attempt += 1
            if attempt < self.max_retries:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying {phase} for {idea_id} in {wait_time}s...")
                await asyncio.sleep(wait_time)

        self.worktree_states[idea_id]['error_history'].append({
            'phase': phase,
            'error': last_error,
            'timestamp': time.time()
        })
        return {'status': 'failed', 'error': last_error}

    async def _process_idea(self, idea_id: str) -> None:
        """Process a complete research idea through all required phases."""
        state = self.worktree_states[idea_id]
        state['status'] = 'procesando'
        state['start_time'] = time.time()
        state['iterations'] += 1
        logger.info(f"Processing idea: {idea_id} - {state['name']}")

        phases = state['metadata'].get('required_phases', [])
        if not phases:
            phases = ['investigacion', 'diseno', 'implementacion', 'evaluacion', 'refinamiento']

        for phase in phases:
            if not self._running:
                logger.warning(f"Processing interrupted for {idea_id}")
                state['status'] = 'interrumpido'
                break

            # Handle pause
            while self._paused and self._running:
                logger.debug(f"Paused during {phase} for {idea_id}")
                await asyncio.sleep(1)

            result = await self._execute_phase(idea_id, phase)
            state['results'][phase] = result

            if result['status'] == 'failed':
                state['status'] = 'error'
                logger.error(f"Failed to process {idea_id}: {result.get('error')}")
                return
            elif result['status'] == 'skipped':
                logger.warning(f"Skipped phase {phase} for {idea_id}")
                continue

            self._update_dashboard(idea_id, phase, result)

        state['status'] = 'completado'
        state['current_phase'] = None
        logger.success(f"Completed idea: {idea_id}")

    def _get_next_pending_idea(self) -> Optional[str]:
        """Select the next pending idea based on priority and FIFO."""
        pending = []
        for idea_id, state in self.worktree_states.items():
            if state['status'] == 'pendiente':
                priority = state['metadata'].get('priority', 'media')
                pending.append((idea_id, priority))

        if not pending:
            return None

        # Sort by priority (alta > media > baja) then by id (FIFO)
        priority_order = {'alta': 0, 'media': 1, 'baja': 2}
        pending.sort(key=lambda x: (priority_order.get(x[1], 1), x[0]))
        return pending[0][0]

    def _update_dashboard(self, idea_id: str, phase: str, result: Dict[str, Any]) -> None:
        """Update dashboard with progress if callback is configured."""
        if self.dashboard_callback:
            try:
                if asyncio.iscoroutinefunction(self.dashboard_callback):
                    asyncio.create_task(self.dashboard_callback({
                        'idea_id': idea_id,
                        'phase': phase,
                        'result': result,
                        'timestamp': time.time()
                    }))
                else:
                    self.dashboard_callback({
                        'idea_id': idea_id,
                        'phase': phase,
                        'result': result,
                        'timestamp': time.time()
                    })
            except Exception as e:
                logger.warning(f"Dashboard update failed: {e}")

    async def _checkpoint_loop(self) -> None:
        """Background task that saves checkpoints periodically."""
        while self._running:
            await asyncio.sleep(self.checkpoint_interval)
            if not self._paused:
                self._save_checkpoint()

    def _save_checkpoint(self) -> None:
        """Save current state checkpoint."""
        checkpoint = {
            'timestamp': time.time(),
            'worktree_states': self.worktree_states,
            'current_idea_id': self._current_idea_id,
            'running': self._running,
            'paused': self._paused
        }
        checkpoint_path = Path(self.config.get('checkpoint_path', 'data/checkpoint.json'))
        try:
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Checkpoint saved to {checkpoint_path}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def load_checkpoint(self, path: str) -> bool:
        """Load state from checkpoint."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            self.worktree_states = checkpoint.get('worktree_states', {})
            self._current_idea_id = checkpoint.get('current_idea_id')
            self._paused = checkpoint.get('paused', False)
            logger.info(f"Loaded checkpoint from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False

    async def _main_loop(self) -> None:
        """Main processing loop."""
        logger.info("Main loop started")
        while self._running:
            # Handle pause
            while self._paused:
                logger.debug("Main loop paused")
                await asyncio.sleep(1)
                if not self._running:
                    return

            # Find next pending idea
            idea_id = self._get_next_pending_idea()
            if not idea_id:
                logger.info("No more pending ideas. Main loop finished.")
                self._running = False
                break

            self._current_idea_id = idea_id
            await self._process_idea(idea_id)
            self._current_idea_id = None

            # Brief pause between ideas
            await asyncio.sleep(1)

        logger.info("Main loop ended")

    def start_loop(self) -> None:
        """Start the main processing loop."""
        if self._running:
            logger.warning("Loop already running")
            return

        self._running = True
        self._paused = False
        logger.info("Starting orchestrator loop")

        try:
            loop = asyncio.get_event_loop()
            self._main_loop_task = loop.create_task(self._main_loop())
            self._checkpoint_task = loop.create_task(self._checkpoint_loop())
        except RuntimeError:
            # If no event loop is running, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._main_loop_task = loop.create_task(self._main_loop())
            self._checkpoint_task = loop.create_task(self._checkpoint_loop())
            loop.run_forever()

    def pause_loop(self) -> None:
        """Pause the main loop."""
        if not self._running:
            logger.warning("Cannot pause: loop not running")
            return
        self._paused = True
        logger.info("Orchestrator loop paused")

    def resume_loop(self) -> None:
        """Resume the main loop."""
        if not self._running:
            logger.warning("Cannot resume: loop not running")
            return
        self._paused = False
        logger.info("Orchestrator loop resumed")

    def stop_loop(self) -> None:
        """Stop the main loop."""
        self._running = False
        self._paused = False
        logger.info("Orchestrator loop stopping...")

        if self._main_loop_task and not self._main_loop_task.done():
            self._main_loop_task.cancel()
        if self._checkpoint_task and not self._checkpoint_task.done():
            self._checkpoint_task.cancel()

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        total = len(self.worktree_states)
        status_counts = {}
        for state in self.worktree_states.values():
            s = state['status']
            status_counts[s] = status_counts.get(s, 0) + 1

        return {
            'running': self._running,
            'paused': self._paused,
            'current_idea_id': self._current_idea_id,
            'total_ideas': total,
            'status_counts': status_counts,
            'registered_agents': list(self.agents.keys()),
            'worktree_states': {
                idea_id: {
                    'id': s['id'],
                    'name': s['name'],
                    'status': s['status'],
                    'current_phase': s['current_phase'],
                    'iterations': s['iterations'],
                    'last_update': s['last_update']
                }
                for idea_id, s in self.worktree_states.items()
            }
        }

    def get_idea_status(self, idea_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for a specific idea."""
        return self.worktree_states.get(idea_id)

    async def run_single_idea(self, idea_id: str) -> Dict[str, Any]:
        """Run a single idea synchronously (for testing/manual execution)."""
        if idea_id not in self.worktree_states:
            raise ValueError(f"Unknown idea_id: {idea_id}")

        self.worktree_states[idea_id]['status'] = 'procesando'
        await self._process_idea(idea_id)
        return self.worktree_states[idea_id]

    def __repr__(self) -> str:
        return (
            f"OrchestratorAgent(ideas={len(self.worktree_states)}, "
            f"agents={list(self.agents.keys())}, running={self._running})"
        )