"""State manager for 70 worktree ideas with persistence, priorities and thread-safety."""

from typing import Dict, Any, List, Optional, Callable
import time
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger


class WorktreeManager:
    """Manages state for 70 pharmaceutical research worktrees with persistence."""

    MAX_WORKTREES = 70
    DEFAULT_TIMEOUT = 86400  # 24 hours
    CHECKPOINT_INTERVAL = 300  # 5 minutes

    PHASES = [
        'investigacion', 'diseno', 'implementacion', 'evaluacion', 'refinamiento', 'completado'
    ]

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._lock = threading.Lock()
        self.worktrees: Dict[str, Dict[str, Any]] = {}
        self._checkpoint_timer: Optional[threading.Timer] = None
        self._running = False

        # Configuration
        self.data_dir = Path(self.config.get('data_dir', 'data'))
        self.checkpoint_interval = self.config.get('checkpoint_interval', self.CHECKPOINT_INTERVAL)
        self.worktree_timeout = self.config.get('worktree_timeout', self.DEFAULT_TIMEOUT)
        self.max_retries = self.config.get('max_retries', 3)
        self.auto_checkpoint = self.config.get('auto_checkpoint', True)

        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Try to restore from checkpoint
        self._restore_state()
        self._start_auto_checkpoint()

        logger.info(
            f"WorktreeManager initialized: {len(self.worktrees)} worktrees loaded, "
            f"max={self.MAX_WORKTREES}, checkpoint_interval={self.checkpoint_interval}s"
        )

    # ─── Persistence ───────────────────────────────────────────

    def _state_path(self) -> Path:
        """Get state file path."""
        return self.data_dir / 'worktree_state.json'

    def _checkpoint_path(self, worktree_id: str = None) -> Path:
        """Get checkpoint file path."""
        checkpoint_dir = self.data_dir / 'checkpoints'
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        if worktree_id:
            return checkpoint_dir / f"{worktree_id}_checkpoint.json"
        return checkpoint_dir / "state_checkpoint.json"

    def _save_state(self) -> None:
        """Save current state to disk."""
        with self._lock:
            try:
                state = {
                    'worktrees': self.worktrees,
                    'metadata': {
                        'total': len(self.worktrees),
                        'pending': self._count_by_status('pendiente'),
                        'processing': self._count_by_status('procesando'),
                        'completed': self._count_by_status('completado'),
                        'failed': self._count_by_status('error'),
                        'last_save': time.time()
                    }
                }
                with open(self._state_path(), 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2, ensure_ascii=False, default=str)
                logger.debug(f"State saved: {len(self.worktrees)} worktrees")
            except Exception as e:
                logger.error(f"Failed to save state: {e}")

    def _save_worktree_checkpoint(self, worktree_id: str) -> None:
        """Save checkpoint for a specific worktree."""
        with self._lock:
            try:
                if worktree_id in self.worktrees:
                    checkpoint = {
                        'worktree': self.worktrees[worktree_id],
                        'timestamp': time.time(),
                        'id': worktree_id
                    }
                    with open(self._checkpoint_path(worktree_id), 'w', encoding='utf-8') as f:
                        json.dump(checkpoint, f, indent=2, ensure_ascii=False, default=str)
                    self.worktrees[worktree_id]['last_checkpoint'] = time.time()
                    logger.debug(f"Checkpoint saved for {worktree_id}")
            except Exception as e:
                logger.error(f"Failed to save checkpoint for {worktree_id}: {e}")

    def _restore_state(self) -> None:
        """Restore state from disk on initialization."""
        try:
            if self._state_path().exists():
                with open(self._state_path(), 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self.worktrees = state.get('worktrees', {})
                logger.info(f"Restored state: {len(self.worktrees)} worktrees")

                # Mark processing worktrees as pending (they were interrupted)
                for wid, w in self.worktrees.items():
                    if w.get('status') == 'procesando':
                        w['status'] = 'pendiente'
                        w['interrupted'] = True
                        logger.warning(f"Worktree {wid} marked as interrupted")
        except Exception as e:
            logger.error(f"Failed to restore state: {e}")
            self.worktrees = {}

    def _start_auto_checkpoint(self) -> None:
        """Start automatic checkpoint timer."""
        if self.auto_checkpoint and not self._running:
            self._running = True
            self._schedule_checkpoint()

    def _schedule_checkpoint(self) -> None:
        """Schedule next checkpoint."""
        if self._running:
            self._checkpoint_timer = threading.Timer(self.checkpoint_interval, self._do_auto_checkpoint)
            self._checkpoint_timer.daemon = True
            self._checkpoint_timer.start()

    def _do_auto_checkpoint(self) -> None:
        """Perform periodic checkpoint."""
        try:
            self._save_state()
            # Save individual checkpoints for active worktrees
            for wid, w in self.worktrees.items():
                if w.get('status') in ('procesando', 'completado'):
                    self._save_worktree_checkpoint(wid)
        finally:
            self._schedule_checkpoint()

    def stop_auto_checkpoint(self) -> None:
        """Stop automatic checkpointing."""
        self._running = False
        if self._checkpoint_timer:
            self._checkpoint_timer.cancel()
        # Save final state
        self._save_state()
        logger.info("Auto-checkpoint stopped")

    # ─── Worktree CRUD ─────────────────────────────────────────

    def create_worktree(self, drug: str, disease: str,
                       priority: str = 'media',
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new worktree idea.

        Args:
            drug: Drug/candidate name
            disease: Target disease
            priority: Priority level ('alta', 'media', 'baja')
            metadata: Additional metadata

        Returns:
            Created worktree dictionary
        """
        with self._lock:
            if len(self.worktrees) >= self.MAX_WORKTREES:
                logger.warning(f"Max worktrees reached ({self.MAX_WORKTREES})")
                # Remove oldest completed/failed worktree to make space
                oldest = self._find_oldest_completed()
                if oldest:
                    del self.worktrees[oldest]
                    logger.info(f"Replaced old worktree: {oldest}")

            worktree_id = f"wt_{len(self.worktrees) + 1:04d}_{int(time.time())}"

            worktree = {
                'id': worktree_id,
                'drug_name': drug,
                'target_disease': disease,
                'priority': priority if priority in ('alta', 'media', 'baja') else 'media',
                'status': 'pendiente',
                'phase': None,
                'results': {},
                'iterations': 0,
                'retry_count': 0,
                'max_retries': self.max_retries,
                'created_at': time.time(),
                'updated_at': time.time(),
                'started_at': None,
                'completed_at': None,
                'last_checkpoint': None,
                'interrupted': False,
                'timeout': self.worktree_timeout,
                'confidence_score': 0,
                'relevance_score': 0,
                'metadata': metadata or {},
                'metrics_history': [],
                'error_log': []
            }

            self.worktrees[worktree_id] = worktree
            self._save_state()
            logger.info(f"Created worktree: {worktree_id} ({drug} -> {disease})")
            return worktree

    def get_worktree(self, worktree_id: str) -> Optional[Dict[str, Any]]:
        """Get worktree by ID."""
        with self._lock:
            return self.worktrees.get(worktree_id)

    def update_phase(self, worktree_id: str, phase: str) -> bool:
        """
        Update current phase of a worktree.

        Args:
            worktree_id: Worktree identifier
            phase: Phase name

        Returns:
            Success boolean
        """
        with self._lock:
            if worktree_id not in self.worktrees:
                logger.warning(f"Worktree not found: {worktree_id}")
                return False

            if phase not in self.PHASES:
                logger.warning(f"Invalid phase: {phase}")
                return False

            current_phase = self.worktrees[worktree_id].get('phase')

            # Validate phase progression
            if current_phase and current_phase in self.PHASES:
                current_idx = self.PHASES.index(current_phase)
                new_idx = self.PHASES.index(phase)
                if new_idx < current_idx:
                    logger.warning(f"Cannot regress phase: {current_phase} -> {phase}")
                    return False

            self.worktrees[worktree_id]['phase'] = phase
            self.worktrees[worktree_id]['updated_at'] = time.time()

            if phase == 'completado':
                self.worktrees[worktree_id]['status'] = 'completado'
                self.worktrees[worktree_id]['completed_at'] = time.time()

            # Save checkpoint after phase change
            self._save_worktree_checkpoint(worktree_id)
            logger.info(f"Worktree {worktree_id} phase: {current_phase} -> {phase}")
            return True

    def update_status(self, worktree_id: str, status: str) -> bool:
        """
        Update status of a worktree.

        Args:
            worktree_id: Worktree identifier
            status: New status

        Returns:
            Success boolean
        """
        valid_statuses = ['pendiente', 'procesando', 'completado', 'error', 'interrumpido']
        if status not in valid_statuses:
            logger.warning(f"Invalid status: {status}")
            return False

        with self._lock:
            if worktree_id not in self.worktrees:
                logger.warning(f"Worktree not found: {worktree_id}")
                return False

            old_status = self.worktrees[worktree_id]['status']
            self.worktrees[worktree_id]['status'] = status
            self.worktrees[worktree_id]['updated_at'] = time.time()

            if status == 'procesando' and old_status != 'procesando':
                self.worktrees[worktree_id]['started_at'] = time.time()
                self.worktrees[worktree_id]['iterations'] += 1

                # Auto-retry: increment retry count on error->processing
                if old_status == 'error':
                    self.worktrees[worktree_id]['retry_count'] += 1

            if status == 'completado':
                self.worktrees[worktree_id]['completed_at'] = time.time()

            self._save_worktree_checkpoint(worktree_id)
            logger.info(f"Worktree {worktree_id} status: {old_status} -> {status}")
            return True

    def save_results(self, worktree_id: str, results: Dict[str, Any]) -> bool:
        """
        Save execution results for a worktree.

        Args:
            worktree_id: Worktree identifier
            results: Results dictionary

        Returns:
            Success boolean
        """
        with self._lock:
            if worktree_id not in self.worktrees:
                logger.warning(f"Worktree not found: {worktree_id}")
                return False

            # Merge results, preserving history
            old_results = self.worktrees[worktree_id].get('results', {})
            for key, value in results.items():
                if isinstance(value, dict) and key in old_results:
                    old_results[key].update(value)
                else:
                    old_results[key] = value

            self.worktrees[worktree_id]['results'] = old_results
            self.worktrees[worktree_id]['updated_at'] = time.time()

            # Track metrics history
            if 'metrics_history' not in self.worktrees[worktree_id]:
                self.worktrees[worktree_id]['metrics_history'] = []
            metrics = results.get('metrics', results.get('summary', {}))
            if isinstance(metrics, dict) and 'r2' in metrics:
                self.worktrees[worktree_id]['metrics_history'].append({
                    'timestamp': time.time(),
                    'iteration': self.worktrees[worktree_id]['iterations'],
                    'metrics': metrics
                })

            # Update confidence/relevance scores if available
            if 'confidence_score' in results:
                self.worktrees[worktree_id]['confidence_score'] = results['confidence_score']
            if 'relevance_score' in results:
                self.worktrees[worktree_id]['relevance_score'] = results['relevance_score']

            self._save_worktree_checkpoint(worktree_id)
            logger.info(f"Results saved for {worktree_id}")
            return True

    def log_error(self, worktree_id: str, error: str) -> None:
        """Log error for a worktree."""
        with self._lock:
            if worktree_id in self.worktrees:
                self.worktrees[worktree_id]['error_log'].append({
                    'timestamp': time.time(),
                    'error': str(error)
                })
                logger.error(f"Error logged for {worktree_id}: {error[:100]}")

    # ─── Query Methods ─────────────────────────────────────────

    def get_pending_worktrees(self) -> List[Dict[str, Any]]:
        """
        Get list of pending worktrees, sorted by priority.

        Returns:
            Sorted list of pending worktrees
        """
        with self._lock:
            pending = []
            now = time.time()

            for wid, w in self.worktrees.items():
                if w.get('status') != 'pendiente':
                    continue

                # Check timeout
                started = w.get('started_at')
                if started and (now - started) > w.get('timeout', self.worktree_timeout):
                    w['status'] = 'interrumpido'
                    w['error_log'].append({
                        'timestamp': now,
                        'error': f'Timeout after {(now - started) / 3600:.1f}h'
                    })
                    continue

                # Check retry limit
                if w.get('retry_count', 0) >= w.get('max_retries', self.max_retries):
                    continue

                pending.append(w)

            # Sort by priority (alta > media > baja) then by creation time (FIFO)
            priority_order = {'alta': 0, 'media': 1, 'baja': 2}
            pending.sort(key=lambda x: (priority_order.get(x.get('priority', 'media'), 1),
                                        x.get('retry_count', 0),
                                        x.get('created_at', 0)))

            return pending

    def get_completed_worktrees(self) -> List[Dict[str, Any]]:
        """Get list of completed worktrees, sorted by completion time."""
        with self._lock:
            completed = [w for w in self.worktrees.values() if w.get('status') == 'completado']
            completed.sort(key=lambda x: x.get('completed_at', 0), reverse=True)
            return completed

    def get_failed_worktrees(self) -> List[Dict[str, Any]]:
        """Get list of failed worktrees."""
        with self._lock:
            return [w for w in self.worktrees.values() if w.get('status') == 'error']

    def get_active_worktrees(self) -> List[Dict[str, Any]]:
        """Get list of currently processing worktrees."""
        with self._lock:
            return [w for w in self.worktrees.values() if w.get('status') == 'procesando']

    def get_top_candidates(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top N candidates by combined score.

        Args:
            n: Number of top candidates

        Returns:
            Sorted list of top candidates
        """
        with self._lock:
            completed = self.get_completed_worktrees()
            scored = [w for w in completed if w.get('confidence_score', 0) > 50]
            scored.sort(key=lambda x: x.get('confidence_score', 0) * 0.7 +
                                      x.get('relevance_score', 0) * 0.3,
                       reverse=True)
            return scored[:n]

    # ─── Status & Statistics ───────────────────────────────────

    def _count_by_status(self, status: str) -> int:
        """Count worktrees by status."""
        return sum(1 for w in self.worktrees.values() if w.get('status') == status)

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        with self._lock:
            total = len(self.worktrees)
            completed = self._count_by_status('completado')
            failed = self._count_by_status('error')
            processing = self._count_by_status('procesando')
            pending = self._count_by_status('pendiente')
            interrupted = self._count_by_status('interrumpido')

            success_rate = (completed / max(total, 1)) * 100
            avg_score = 0
            if completed > 0:
                scores = [w.get('confidence_score', 0) for w in self.worktrees.values()
                         if w.get('status') == 'completado']
                avg_score = sum(scores) / len(scores) if scores else 0

            priority_distribution = {'alta': 0, 'media': 0, 'baja': 0}
            for w in self.worktrees.values():
                p = w.get('priority', 'media')
                priority_distribution[p] = priority_distribution.get(p, 0) + 1

            return {
                'total': total,
                'completed': completed,
                'failed': failed,
                'processing': processing,
                'pending': pending,
                'interrupted': interrupted,
                'success_rate': round(success_rate, 1),
                'average_confidence_score': round(avg_score, 1),
                'priority_distribution': priority_distribution,
                'phases_completed': {
                    phase: sum(1 for w in self.worktrees.values()
                             if w.get('phase') == phase or phase in w.get('results', {}))
                    for phase in self.PHASES
                },
                'last_updated': time.time()
            }

    def _find_oldest_completed(self) -> Optional[str]:
        """Find oldest completed/failed worktree for replacement."""
        candidates = []
        for wid, w in self.worktrees.items():
            if w.get('status') in ('completado', 'error'):
                candidates.append((w.get('completed_at', 0) or w.get('updated_at', 0), wid))
        if candidates:
            candidates.sort()
            return candidates[0][1]
        return None

    # ─── Export Methods ────────────────────────────────────────

    def export_report(self, format: str = 'json') -> str:
        """
        Export worktree report.

        Args:
            format: Export format ('json', 'csv')

        Returns:
            Path to exported file
        """
        export_dir = self.data_dir / 'exports'
        export_dir.mkdir(parents=True, exist_ok=True)

        timestamp = int(time.time())

        if format == 'json':
            path = export_dir / f"worktree_report_{timestamp}.json"
            with self._lock:
                report = {
                    'generated_at': time.time(),
                    'statistics': self.get_statistics(),
                    'worktrees': {
                        wid: {
                            k: w[k]
                            for k in ['id', 'drug_name', 'target_disease', 'status',
                                     'phase', 'iterations', 'confidence_score',
                                     'relevance_score', 'created_at', 'completed_at']
                            if k in w
                        }
                        for wid, w in self.worktrees.items()
                    }
                }
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        elif format == 'csv':
            path = export_dir / f"worktree_report_{timestamp}.csv"
            with self._lock:
                lines = [
                    'id,drug_name,target_disease,status,phase,iterations,confidence_score,relevance_score,created_at,completed_at'
                ]
                for wid, w in self.worktrees.items():
                    lines.append(
                        f"{wid},{w.get('drug_name','')},{w.get('target_disease','')},"
                        f"{w.get('status','')},{w.get('phase','')},{w.get('iterations',0)},"
                        f"{w.get('confidence_score',0)},{w.get('relevance_score',0)},"
                        f"{w.get('created_at','')},{w.get('completed_at','')}"
                    )
                with open(path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))

        else:
            logger.error(f"Unsupported export format: {format}")
            return ""

        logger.success(f"Report exported: {path}")
        return str(path)

    def get_worktree_summary(self, worktree_id: str) -> Optional[str]:
        """Get human-readable summary of a worktree."""
        w = self.get_worktree(worktree_id)
        if not w:
            return None

        created = datetime.fromtimestamp(w['created_at']).strftime('%Y-%m-%d %H:%M')
        duration = ""
        if w.get('started_at') and w.get('completed_at'):
            secs = w['completed_at'] - w['started_at']
            hours = int(secs // 3600)
            mins = int((secs % 3600) // 60)
            duration = f"{hours}h {mins}m"

        summary = (
            f"═══════════════════════════════════════\n"
            f"  Worktree: {worktree_id}\n"
            f"  Fármaco: {w.get('drug_name', '?')}\n"
            f"  Enfermedad: {w.get('target_disease', '?')}\n"
            f"  Estado: {w.get('status', '?').upper()}\n"
            f"  Fase: {w.get('phase', 'N/A')}\n"
            f"  Prioridad: {w.get('priority', 'media')}\n"
            f"  Iteraciones: {w.get('iterations', 0)}\n"
            f"  Score Confianza: {w.get('confidence_score', 0)}/100\n"
            f"  Score Relevancia: {w.get('relevance_score', 0)}/100\n"
            f"  Creado: {created}\n"
            f"  Duración: {duration or 'N/A'}\n"
            f"  Reintentos: {w.get('retry_count', 0)}/{w.get('max_retries', self.max_retries)}\n"
            f"═══════════════════════════════════════\n"
        )

        return summary

    # ─── Batch Operations ──────────────────────────────────────

    def create_batch_worktrees(self, ideas: List[Dict[str, Any]]) -> List[str]:
        """
        Create multiple worktrees from a list of ideas.

        Args:
            ideas: List of idea dictionaries with 'drug', 'disease', 'priority' keys

        Returns:
            List of created worktree IDs
        """
        created = []
        for idea in ideas:
            wid = self.create_worktree(
                drug=idea.get('drug', 'Unknown'),
                disease=idea.get('disease', 'Unknown'),
                priority=idea.get('priority', 'media'),
                metadata=idea.get('metadata')
            )
            created.append(wid['id'])
        return created

    def reset_worktree(self, worktree_id: str) -> bool:
        """Reset a worktree to initial state."""
        with self._lock:
            if worktree_id not in self.worktrees:
                return False
            w = self.worktrees[worktree_id]
            w['status'] = 'pendiente'
            w['phase'] = None
            w['results'] = {}
            w['iterations'] = 0
            w['retry_count'] = 0
            w['started_at'] = None
            w['completed_at'] = None
            w['confidence_score'] = 0
            w['relevance_score'] = 0
            w['updated_at'] = time.time()
            logger.info(f"Worktree {worktree_id} reset")
            return True

    def bulk_update_status(self, status: str, filter_condition: Callable = None) -> int:
        """
        Bulk update worktree status.

        Args:
            status: Target status
            filter_condition: Optional filter function

        Returns:
            Number of updated worktrees
        """
        count = 0
        with self._lock:
            for wid, w in self.worktrees.items():
                if filter_condition and not filter_condition(w):
                    continue
                w['status'] = status
                w['updated_at'] = time.time()
                count += 1
        if count:
            logger.info(f"Bulk updated {count} worktrees to {status}")
        return count

    # ─── Cleanup ──────────────────────────────────────────────

    def cleanup_old_worktrees(self, max_age_days: int = 30) -> int:
        """Remove worktrees older than specified days."""
        cutoff = time.time() - (max_age_days * 86400)
        count = 0

        with self._lock:
            to_remove = [
                wid for wid, w in self.worktrees.items()
                if w.get('updated_at', 0) < cutoff
            ]
            for wid in to_remove:
                del self.worktrees[wid]
                count += 1

        if count:
            # Clean up old checkpoint files
            checkpoint_dir = self.data_dir / 'checkpoints'
            for cp in checkpoint_dir.glob('*_checkpoint.json'):
                if cp.stat().st_mtime < cutoff:
                    cp.unlink()

            logger.info(f"Cleaned up {count} old worktrees (>{max_age_days}d)")
        return count

    def __repr__(self) -> str:
        stats = self.get_statistics()
        return (
            f"WorktreeManager(worktrees={stats['total']}, "
            f"completed={stats['completed']}, pending={stats['pending']}, "
            f"processing={stats['processing']}, failed={stats['failed']})"
        )

    def __del__(self):
        self.stop_auto_checkpoint()