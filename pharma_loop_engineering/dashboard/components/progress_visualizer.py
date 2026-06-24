"""Progress visualization generator for dashboard."""

from typing import Dict, Any, List, Optional, Tuple
import time
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from loguru import logger


class ProgressVisualizer:
    """Generator for progress visualizations and reports."""

    # Color scheme
    COLORS = {
        'primary': '#1E3A8A',
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'neutral': '#6B7280',
        'phases': {
            'investigacion': '#3B82F6',
            'diseno': '#8B5CF6',
            'implementacion': '#F59E0B',
            'evaluacion': '#10B981',
            'refinamiento': '#EF4444'
        }
    }

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.output_dir = Path(self.config.get('output_dir', 'data/results/visualizations'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ProgressVisualizer initialized, output: {self.output_dir}")

    def _get_output_path(self, worktree_id: str, viz_type: str, timestamp: int = None) -> Path:
        """Generate standardized output path."""
        if timestamp is None:
            timestamp = int(time.time())
        filename = f"{worktree_id}_{timestamp}_{viz_type}.png"
        return self.output_dir / filename

    def generate_progress_infographic(self, worktree_data: Dict[str, Any]) -> Optional[Path]:
        """
        Generate progress infographic for a single worktree.

        Args:
            worktree_data: Dictionary with worktree state information

        Returns:
            Path to generated image
        """
        worktree_id = worktree_data.get('id', 'unknown')
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle(f"Progreso: {worktree_data.get('name', 'Unknown')}", 
                        fontsize=16, fontweight='bold', color=self.COLORS['primary'])

            # 1. Phase progress (top-left)
            ax1 = axes[0, 0]
            phases = ['investigacion', 'diseno', 'implementacion', 'evaluacion', 'refinamiento']
            current_phase = worktree_data.get('current_phase', 'pendiente')
            status = worktree_data.get('status', 'pendiente')

            phase_colors = [self.COLORS['phases'].get(p, self.COLORS['neutral']) for p in phases]
            if current_phase in phases:
                idx = phases.index(current_phase)
                phase_colors[idx] = self.COLORS['warning']

            ax1.barh(phases, [1]*5, color=phase_colors, edgecolor='black', linewidth=0.5)
            ax1.set_xlim(0, 1.5)
            ax1.set_xticks([])
            ax1.set_title(f"Fase Actual: {current_phase.upper()}", fontweight='bold')
            ax1.set_yticklabels(phases, rotation=0)

            # Add status badge
            status_color = self.COLORS['success'] if status == 'completado' else (
                self.COLORS['warning'] if status == 'procesando' else self.COLORS['neutral']
            )
            ax1.text(0.75, 4.5, status.upper(), fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor=status_color, alpha=0.8))

            # 2. Score evolution (top-right)
            ax2 = axes[0, 1]
            iterations = worktree_data.get('iterations', 0)
            score = worktree_data.get('confidence_score', 0)

            # Simulate evolution if single data point
            if iterations > 0:
                scores = np.linspace(max(0, score - 20), score, iterations)
                ax2.plot(range(1, iterations + 1), scores, marker='o', 
                        color=self.COLORS['primary'], linewidth=2, markersize=8)
                ax2.fill_between(range(1, iterations + 1), scores, alpha=0.3, color=self.COLORS['primary'])
            else:
                ax2.bar(['Inicio'], [score], color=self.COLORS['primary'], alpha=0.7)

            ax2.set_xlabel('Iteración')
            ax2.set_ylabel('Score de Confianza')
            ax2.set_title('Evolución del Score', fontweight='bold')
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3, linestyle='--')

            # 3. Metrics radar (bottom-left)
            ax3 = axes[1, 0]
            metrics = worktree_data.get('metrics', {})
            metric_names = ['r2', 'rmse', 'mae', 'auc_roc']
            metric_values = [metrics.get(m, 0) for m in metric_names]

            # Normalize for radar chart
            max_vals = {'r2': 1.0, 'rmse': 2.0, 'mae': 1.0, 'auc_roc': 1.0}
            normalized = [min(metric_values[i] / max_vals.get(metric_names[i], 1), 1) 
                         for i in range(len(metric_names))]

            angles = np.linspace(0, 2 * np.pi, len(metric_names), endpoint=False).tolist()
            normalized += normalized[:1]
            angles += angles[:1]

            ax3 = plt.subplot(2, 2, 3, polar=True)
            ax3.plot(angles, normalized, 'o-', linewidth=2, color=self.COLORS['primary'])
            ax3.fill(angles, normalized, alpha=0.25, color=self.COLORS['primary'])
            ax3.set_xticks(angles[:-1])
            ax3.set_xticklabels(metric_names, fontsize=9)
            ax3.set_ylim(0, 1)
            ax3.set_title('Métricas Normalizadas', fontweight='bold', pad=20)

            # 4. Timeline (bottom-right)
            ax4 = axes[1, 1]
            start_time = worktree_data.get('start_time', time.time() - 3600)
            elapsed = (time.time() - start_time) / 60  # minutes

            time_segments = ['Investigación', 'Diseño', 'Implementación', 'Evaluación']
            segment_durations = [elapsed/5, elapsed/5, elapsed/5, elapsed/5] if elapsed > 0 else [1,1,1,1]

            colors = [self.COLORS['phases'].get(p, self.COLORS['neutral']) for p in time_segments]
            ax4.barh(time_segments, segment_durations, color=colors, edgecolor='black', linewidth=0.5)
            ax4.set_xlabel('Minutos')
            ax4.set_title(f'Tiempo Transcurrido: {elapsed:.1f} min', fontweight='bold')
            ax4.invert_yaxis()

            plt.tight_layout()
            
            output_path = self._get_output_path(worktree_id, 'progress_infographic')
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0F172A')
            plt.close()

            logger.success(f"Generated progress infographic: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate progress infographic: {e}")
            return None

    def generate_score_evolution_chart(self, worktree_id: str, 
                                      iteration_scores: List[Tuple[int, float]]) -> Optional[Path]:
        """
        Generate score evolution chart across iterations.

        Args:
            worktree_id: Worktree identifier
            iteration_scores: List of (iteration_number, score) tuples

        Returns:
            Path to generated image
        """
        try:
            if not iteration_scores:
                return None

            iterations, scores = zip(*iteration_scores)

            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Line plot with gradient
            ax.plot(iterations, scores, marker='o', linewidth=3, markersize=10,
                   color=self.COLORS['primary'], label='Score de Confianza')
            
            # Add trend line
            z = np.polyfit(iterations, scores, 1)
            p = np.poly1d(z)
            ax.plot(iterations, p(iterations), "--", alpha=0.5, 
                   color=self.COLORS['warning'], label='Tendencia')

            # Fill under curve
            ax.fill_between(iterations, scores, alpha=0.3, color=self.COLORS['primary'])

            # Annotations
            for i, (iter_num, score) in enumerate(iteration_scores):
                color = self.COLORS['success'] if score >= 75 else (
                    self.COLORS['warning'] if score >= 50 else self.COLORS['danger']
                )
                ax.annotate(f'{score:.1f}', (iter_num, score), 
                           textcoords="offset points", xytext=(0, 10), ha='center',
                           fontweight='bold', color=color)

            ax.set_xlabel('Iteración', fontsize=12)
            ax.set_ylabel('Score de Confianza', fontsize=12)
            ax.set_title(f'Evolución del Score - {worktree_id}', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend()

            # Add threshold line
            ax.axhline(y=75, color=self.COLORS['success'], linestyle='--', alpha=0.5, label='Umbral Proceed')
            ax.axhline(y=50, color=self.COLORS['warning'], linestyle='--', alpha=0.5, label='Umbral Refine')

            plt.tight_layout()
            
            output_path = self._get_output_path(worktree_id, 'score_evolution')
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0F172A')
            plt.close()

            logger.success(f"Generated score evolution chart: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate score evolution chart: {e}")
            return None

    def generate_experiment_flowchart(self, worktree_data: Dict[str, Any]) -> Optional[Path]:
        """
        Generate experiment flowchart with colored nodes by status.

        Args:
            worktree_data: Worktree state information

        Returns:
            Path to generated image
        """
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Define phases and their positions
            phases = [
                ('Investigación', 1, 4),
                ('Diseño', 4, 4),
                ('Implementación', 7, 4),
                ('Evaluación', 10, 4),
                ('Refinamiento', 13, 4)
            ]

            current_phase = worktree_data.get('current_phase', 'pendiente')
            status = worktree_data.get('status', 'pendiente')

            # Draw nodes
            for phase_name, x, y in phases:
                phase_key = phase_name.lower()
                
                # Determine node color
                if status == 'completado':
                    color = self.COLORS['success']
                elif phase_key == current_phase:
                    color = self.COLORS['warning']
                elif self._is_phase_completed(phase_key, worktree_data):
                    color = self.COLORS['success']
                else:
                    color = self.COLORS['neutral']

                # Draw node
                circle = plt.Circle((x, y), 0.8, color=color, ec='black', linewidth=2, zorder=3)
                ax.add_patch(circle)
                ax.text(x, y, phase_name[:3].upper(), ha='center', va='center', 
                       fontsize=10, fontweight='bold', color='white', zorder=4)

                # Draw label below
                ax.text(x, y - 1.2, phase_name, ha='center', va='top', 
                       fontsize=9, style='italic')

            # Draw arrows between phases
            for i in range(len(phases) - 1):
                x1, y1 = phases[i][1], phases[i][2]
                x2, y2 = phases[i + 1][1], phases[i + 1][2]
                ax.annotate('', xy=(x2 - 0.8, y), xytext=(x1 + 0.8, y),
                           arrowprops=dict(arrowstyle='->', color='#94A3B8', 
                                          lw=2, connectionstyle='arc3,rad=0'))

            # Add title and status
            ax.set_xlim(0, 15)
            ax.set_ylim(0, 6)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(f"Flujo del Experimento - {worktree_data.get('id', 'Unknown')}\nEstado: {status.upper()}", 
                        fontsize=14, fontweight='bold', pad=20, color=self.COLORS['primary'])

            # Add legend
            legend_elements = [
                mpatches.Patch(color=self.COLORS['success'], label='Completado'),
                mpatches.Patch(color=self.COLORS['warning'], label='En Progreso'),
                mpatches.Patch(color=self.COLORS['neutral'], label='Pendiente')
            ]
            ax.legend(handles=legend_elements, loc='upper left', fontsize=9)

            plt.tight_layout()
            
            output_path = self._get_output_path(worktree_data.get('id', 'unknown'), 'experiment_flowchart')
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0F172A')
            plt.close()

            logger.success(f"Generated experiment flowchart: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate experiment flowchart: {e}")
            return None

    def _is_phase_completed(self, phase: str, worktree_data: Dict[str, Any]) -> bool:
        """Check if a phase is completed based on worktree data."""
        results = worktree_data.get('results', {})
        phase_map = {
            'investigacion': 'investigacion',
            'diseño': 'diseno',
            'implementacion': 'implementacion',
            'evaluacion': 'evaluacion',
            'refinamiento': 'refinamiento'
        }
        
        phase_key = phase_map.get(phase, phase)
        if phase_key in results:
            return results[phase_key].get('status') == 'success'
        return False

    # Plotly-based visualizations

    def generate_correlation_heatmap(self, df: pd.DataFrame, 
                                     output_path: str = None) -> Optional[str]:
        """
        Generate correlation heatmap using plotly.

        Args:
            df: DataFrame with drug-disease scores
            output_path: Custom output path

        Returns:
            Path to saved HTML/image
        """
        try:
            pivot = df.pivot_table(
                values='score',
                index='drug',
                columns='disease',
                aggfunc='mean',
                fill_value=0
            )

            fig = px.imshow(
                pivot.values,
                labels=dict(x="Enfermedad", y="Fármaco", color="Score"),
                x=pivot.columns,
                y=pivot.index,
                color_continuous_scale='Viridis',
                title="Heatmap: Correlación Fármaco-Enfermedad"
            )

            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#0F172A',
                plot_bgcolor='#1E293B',
                font=dict(color='#F1F5F9'),
                height=600
            )

            if output_path is None:
                output_path = self.output_dir / f"correlation_heatmap_{int(time.time())}.html"
            else:
                output_path = Path(output_path)

            fig.write_html(str(output_path))
            logger.success(f"Generated correlation heatmap: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate correlation heatmap: {e}")
            return None

    def generate_top_candidates_bar(self, discoveries: List[Dict[str, Any]], 
                                   top_n: int = 10) -> Optional[str]:
        """
        Generate bar chart of top candidates.

        Args:
            discoveries: List of discovery dictionaries
            top_n: Number of top candidates to show

        Returns:
            Path to saved HTML/image
        """
        try:
            # Sort by relevance score
            discoveries = sorted(discoveries, key=lambda x: x.get('relevance_score', 0), reverse=True)[:top_n]

            drugs = [d.get('drug_candidate', f'Drug {i}') for i, d in enumerate(discoveries)]
            scores = [d.get('relevance_score', 0) for d in discoveries]
            diseases = [d.get('target_disease', 'Unknown') for d in discoveries]

            fig = go.Figure(data=[
                go.Bar(
                    x=drugs,
                    y=scores,
                    text=[f"{s:.1f}" for s in scores],
                    textposition='outside',
                    marker_color=[self.COLORS['primary'] if s >= 70 else 
                                 self.COLORS['warning'] if s >= 50 else 
                                 self.COLORS['danger'] for s in scores],
                    hovertemplate='<b>%{x}</b><br>' +
                                 'Score: %{y:.1f}<br>' +
                                 'Enfermedad: %{customdata}<extra></extra>',
                    customdata=diseases
                )
            ])

            fig.update_layout(
                title=f"Top {top_n} Candidatos a Reposicionamiento",
                xaxis_title="Fármaco",
                yaxis_title="Score de Relevancia",
                template='plotly_dark',
                paper_bgcolor='#0F172A',
                plot_bgcolor='#1E293B',
                font=dict(color='#F1F5F9'),
                height=500,
                yaxis_range=[0, 100]
            )

            output_path = self.output_dir / f"top_candidates_{int(time.time())}.html"
            fig.write_html(str(output_path))
            logger.success(f"Generated top candidates bar chart: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate top candidates bar: {e}")
            return None

    def generate_activity_vs_properties_scatter(self, data: pd.DataFrame,
                                                x_prop: str = 'MW',
                                                y_prop: str = 'LogP',
                                                color_col: str = 'pic50') -> Optional[str]:
        """
        Generate scatter plot of activity vs physicochemical properties.

        Args:
            data: DataFrame with molecular data
            x_prop: Property for x-axis
            y_prop: Property for y-axis
            color_col: Column for color coding

        Returns:
            Path to saved HTML
        """
        try:
            fig = px.scatter(
                data,
                x=x_prop,
                y=y_prop,
                color=color_col,
                size='HeavyAtoms',
                hover_data=['SMILES', 'MW', 'LogP'],
                color_continuous_scale='Viridis',
                title=f"Actividad vs Propiedades: {x_prop} vs {y_prop}",
                labels={x_prop: x_prop, y_prop: y_prop, color_col: 'pIC50'}
            )

            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#0F172A',
                plot_bgcolor='#1E293B',
                font=dict(color='#F1F5F9'),
                height=600
            )

            output_path = self.output_dir / f"scatter_{x_prop}_{y_prop}_{int(time.time())}.html"
            fig.write_html(str(output_path))
            logger.success(f"Generated activity vs properties scatter: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate scatter plot: {e}")
            return None

    def generate_roc_curve(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                          model_name: str = "Model") -> Optional[str]:
        """
        Generate ROC curve for model evaluation.

        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            model_name: Name of the model

        Returns:
            Path to saved HTML
        """
        try:
            from sklearn.metrics import roc_curve, auc

            fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
            roc_auc = auc(fpr, tpr)

            fig = go.Figure()

            # ROC curve
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr,
                mode='lines',
                name=f'{model_name} (AUC = {roc_auc:.3f})',
                line=dict(color=self.COLORS['primary'], width=2)
            ))

            # Diagonal line
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode='lines',
                name='Random (AUC = 0.5)',
                line=dict(color=self.COLORS['neutral'], width=1, dash='dash')
            ))

            fig.update_layout(
                title=f'Curva ROC - {model_name}',
                xaxis_title='Tasa de Falsos Positivos',
                yaxis_title='Tasa de Verdaderos Positivos',
                template='plotly_dark',
                paper_bgcolor='#0F172A',
                plot_bgcolor='#1E293B',
                font=dict(color='#F1F5F9'),
                height=500,
                xaxis=dict(range=[0, 1]),
                yaxis=dict(range=[0, 1])
            )

            output_path = self.output_dir / f"roc_curve_{model_name.replace(' ', '_')}_{int(time.time())}.html"
            fig.write_html(str(output_path))
            logger.success(f"Generated ROC curve: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate ROC curve: {e}")
            return None

    def generate_summary_image(self, worktree_data: Dict[str, Any]) -> Optional[Path]:
        """
        Generate a summary image for a completed worktree.

        Args:
            worktree_data: Completed worktree information

        Returns:
            Path to generated image
        """
        worktree_id = worktree_data.get('id', 'unknown')

        try:
            fig = plt.figure(figsize=(16, 10))
            fig.patch.set_facecolor('#0F172A')

            # Title
            fig.suptitle(f"Reporte Final: {worktree_data.get('name', 'Unknown')}", 
                        fontsize=18, fontweight='bold', color='#F1F5F9', y=0.98)

            # Create grid
            gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3,
                                 left=0.1, right=0.95, top=0.9, bottom=0.1)

            # 1. Key Metrics (top-left, spans 2 columns)
            ax_metrics = fig.add_subplot(gs[0, :2])
            ax_metrics.axis('off')
            ax_metrics.set_facecolor('#1E293B')

            metrics = worktree_data.get('results', {}).get('evaluacion', {}).get('metrics', {})
            score = worktree_data.get('confidence_score', 0)
            status = worktree_data.get('status', 'unknown')

            metrics_text = f"""
            Score Final: {score:.1f}/100 | Estado: {status.upper()}
            
            Métricas Principales:
            • R²: {metrics.get('r2', 0):.3f}
            • RMSE: {metrics.get('rmse', 0):.3f}
            • MAE: {metrics.get('mae', 0):.3f}
            """
            ax_metrics.text(0.1, 0.5, metrics_text, fontsize=12, color='#F1F5F9',
                           verticalalignment='center', fontfamily='monospace',
                           bbox=dict(boxstyle='round', facecolor=self.COLORS['primary'], alpha=0.3))

            # 2. Phase completion pie chart (top-right)
            ax_pie = fig.add_subplot(gs[0, 2])
            phases_completed = sum(1 for r in worktree_data.get('results', {}).values() 
                                  if r.get('status') == 'success')
            phases_total = len(worktree_data.get('results', {}))

            if phases_total > 0:
                sizes = [phases_completed, phases_total - phases_completed]
                colors = [self.COLORS['success'], self.COLORS['neutral']]
                ax_pie.pie(sizes, colors=colors, autopct='%1.0f%%', startangle=90,
                          textprops={'color': 'white', 'fontweight': 'bold'})
                ax_pie.set_title('Fases Completadas', color='#F1F5F9', fontweight='bold')

            # 3. Iterations timeline (middle-left)
            ax_time = fig.add_subplot(gs[1, 0])
            iterations = worktree_data.get('iterations', 0)
            ax_time.barh(['Iteraciones'], [iterations], color=self.COLORS['primary'])
            ax_time.set_xlim(0, max(iterations + 1, 5))
            ax_time.set_title('Total Iteraciones', color='#F1F5F9', fontweight='bold')
            ax_time.tick_params(colors='#F1F5F9')

            # 4. Confidence score gauge (middle-center)
            ax_gauge = fig.add_subplot(gs[1, 1])
            score = worktree_data.get('confidence_score', 0)
            theta = np.linspace(0, np.pi, 100)
            r = np.ones_like(theta)
            
            # Background arc
            ax_gauge.fill_between(theta, 0, r, alpha=0.3, color=self.COLORS['neutral'])
            # Score arc
            score_theta = np.linspace(0, np.pi * (score / 100), 100)
            ax_gauge.fill_between(score_theta, 0, 1, alpha=0.8, 
                                 color=self.COLORS['success'] if score >= 75 else 
                                 self.COLORS['warning'] if score >= 50 else self.COLORS['danger'])
            
            ax_gauge.set_xlim(0, np.pi)
            ax_gauge.set_ylim(0, 1.2)
            ax_gauge.set_aspect('equal')
            ax_gauge.axis('off')
            ax_gauge.set_title(f'Score: {score:.0f}/100', color='#F1F5F9', fontweight='bold', y=1.1)

            # 5. Time elapsed (middle-right)
            ax_elapsed = fig.add_subplot(gs[1, 2])
            start_time = worktree_data.get('start_time', time.time() - 3600)
            elapsed_min = (time.time() - start_time) / 60
            ax_elapsed.barh(['Tiempo'], [elapsed_min], color=self.COLORS['warning'])
            ax_elapsed.set_xlabel('Minutos', color='#F1F5F9')
            ax_elapsed.set_title(f'Total: {elapsed_min:.1f} min', color='#F1F5F9', fontweight='bold')
            ax_elapsed.tick_params(colors='#F1F5F9')

            # 6. Recommendations (bottom, spans all columns)
            ax_rec = fig.add_subplot(gs[2, :])
            ax_rec.axis('off')
            ax_rec.set_facecolor('#1E293B')

            recommendation = worktree_data.get('recommendation', {}).get('binary_recommendation', 'N/A')
            rec_color = self.COLORS['success'] if recommendation == 'proceed' else (
                self.COLORS['warning'] if recommendation == 'refine' else self.COLORS['danger']
            )

            rec_text = f"Recomendación: {recommendation.upper()}"
            ax_rec.text(0.5, 0.5, rec_text, fontsize=16, fontweight='bold',
                       color=rec_color, ha='center', va='center',
                       bbox=dict(boxstyle='round', facecolor='#0F172A', alpha=0.8))

            output_path = self._get_output_path(worktree_id, 'summary_report')
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0F172A')
            plt.close()

            logger.success(f"Generated summary image: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate summary image: {e}")
            return None

    def generate_discovery_collage(self, discoveries: List[Dict[str, Any]], 
                                  max_items: int = 6) -> Optional[Path]:
        """
        Generate collage of daily discoveries.

        Args:
            discoveries: List of discovery dictionaries
            max_items: Maximum number of discoveries to include

        Returns:
            Path to generated image
        """
        try:
            discoveries = discoveries[:max_items]
            n_items = len(discoveries)

            if n_items == 0:
                return None

            # Calculate grid dimensions
            cols = min(3, n_items)
            rows = (n_items + cols - 1) // cols

            fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
            fig.suptitle(f"Descubrimientos Destacados ({n_items})", 
                        fontsize=16, fontweight='bold', color=self.COLORS['primary'], y=0.98)

            if rows == 1 and cols == 1:
                axes = np.array([[axes]])
            elif rows == 1:
                axes = axes.reshape(1, -1)
            elif cols == 1:
                axes = axes.reshape(-1, 1)

            for idx, discovery in enumerate(discoveries):
                row = idx // cols
                col = idx % cols
                ax = axes[row, col]

                ax.set_facecolor('#1E293B')
                ax.axis('off')

                drug = discovery.get('drug_candidate', 'Unknown')
                disease = discovery.get('target_disease', 'Unknown')
                score = discovery.get('relevance_score', 0)
                confidence = discovery.get('confidence_score', 0)

                # Create info card
                info_text = f"""
                💊 {drug}
                
                🎯 {disease}
                
                📊 Relevancia: {score:.1f}/100
                
                ✓ Confianza: {confidence:.1f}/100
                """

                ax.text(0.5, 0.5, info_text, transform=ax.transAxes,
                       fontsize=11, color='#F1F5F9', ha='center', va='center',
                       verticalalignment='center', horizontalalignment='center',
                       bbox=dict(boxstyle='round,pad=1', facecolor=self.COLORS['primary'], alpha=0.8),
                       family='monospace')

            # Hide empty subplots
            for idx in range(n_items, rows * cols):
                row = idx // cols
                col = idx % cols
                axes[row, col].axis('off')

            plt.tight_layout()
            
            output_path = self.output_dir / f"discovery_collage_{datetime.now().strftime('%Y%m%d')}.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0F172A')
            plt.close()

            logger.success(f"Generated discovery collage: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate discovery collage: {e}")
            return None

    def generate_project_timeline(self, project_data: List[Dict[str, Any]]) -> Optional[Path]:
        """
        Generate visual timeline of the entire project.

        Args:
            project_data: List of worktree data

        Returns:
            Path to generated image
        """
        try:
            fig, ax = plt.subplots(figsize=(16, 8))
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#0F172A')

            # Prepare timeline data
            timeline_events = []
            for worktree in project_data:
                start = worktree.get('start_time', time.time() - 3600)
                end = worktree.get('last_update', time.time())
                status = worktree.get('status', 'pendiente')

                timeline_events.append({
                    'name': worktree.get('name', 'Unknown')[:30],
                    'start': datetime.fromtimestamp(start),
                    'end': datetime.fromtimestamp(end),
                    'status': status,
                    'drug': worktree.get('drug_candidate', 'Unknown')
                })

            if not timeline_events:
                logger.warning("No events to plot for timeline")
                return None

            # Sort by start time
            timeline_events.sort(key=lambda x: x['start'])

            # Plot bars
            y_positions = range(len(timeline_events))
            for idx, event in enumerate(timeline_events):
                duration = (event['end'] - event['start']).total_seconds() / 3600  # hours
                if duration < 0.1:
                    duration = 0.1

                color = self.COLORS['success'] if event['status'] == 'completado' else (
                    self.COLORS['warning'] if event['status'] == 'procesando' else self.COLORS['neutral']
                )

                ax.barh(idx, duration, left=mpl_dates.date2num(event['start']),
                       color=color, edgecolor='black', linewidth=0.5, height=0.5)

            # Formatting
            ax.set_yticks(y_positions)
            ax.set_yticklabels([e['name'] for e in timeline_events], color='#F1F5F9')
            ax.xaxis.set_major_formatter(mpl_dates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.xticks(rotation=45, color='#F1F5F9')
            ax.set_xlabel('Tiempo', color='#F1F5F9', fontsize=12)
            ax.set_title('Timeline del Proyecto', fontsize=14, fontweight='bold', 
                        color='#F1F5F9', pad=20)
            ax.grid(True, alpha=0.3, linestyle='--', color='#334155')

            # Legend
            legend_elements = [
                mpatches.Patch(color=self.COLORS['success'], label='Completado'),
                mpatches.Patch(color=self.COLORS['warning'], label='En Progreso'),
                mpatches.Patch(color=self.COLORS['neutral'], label='Pendiente')
            ]
            ax.legend(handles=legend_elements, loc='upper left', 
                     facecolor='#1E293B', edgecolor='#334155', labelcolor='#F1F5F9')

            plt.tight_layout()
            
            output_path = self.output_dir / f"project_timeline_{int(time.time())}.png"
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#0F172A')
            plt.close()

            logger.success(f"Generated project timeline: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate project timeline: {e}")
            return None

    def generate_all_visualizations(self, worktree_data: Dict[str, Any]) -> List[str]:
        """
        Generate all standard visualizations for a worktree.

        Args:
            worktree_data: Worktree state information

        Returns:
            List of paths to generated images
        """
        paths = []
        worktree_id = worktree_data.get('id', 'unknown')

        # Progress infographic
        path = self.generate_progress_infographic(worktree_data)
        if path:
            paths.append(str(path))

        # Score evolution (if iteration history available)
        iterations = worktree_data.get('iterations', 0)
        if iterations > 0:
            scores = [(i, worktree_data.get('confidence_score', 0)) for i in range(1, iterations + 1)]
            path = self.generate_score_evolution_chart(worktree_id, scores)
            if path:
                paths.append(str(path))

        # Experiment flowchart
        path = self.generate_experiment_flowchart(worktree_data)
        if path:
            paths.append(str(path))

        return paths

    def __repr__(self) -> str:
        return f"ProgressVisualizer(output_dir={self.output_dir})"


# Import matplotlib dates for timeline
import matplotlib.dates as mpl_dates