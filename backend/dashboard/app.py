"""Streamlit dashboard for real-time pharmaceutical research monitoring."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import base64
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="PharmaLoop Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional dark theme
st.markdown("""
<style>
    :root {
        --primary-blue: #1E3A8A;
        --success-green: #10B981;
        --alert-orange: #F59E0B;
        --dark-bg: #0F172A;
        --card-bg: #1E293B;
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --border-color: #334155;
    }

    .main {
        background-color: var(--dark-bg);
        color: var(--text-primary);
    }

    .stMetric {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1rem;
    }

    .stMetric label {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    .stMetric value {
        color: var(--text-primary);
        font-size: 1.8rem;
        font-weight: bold;
    }

    .progress-bar {
        background-color: var(--border-color);
        border-radius: 10px;
        height: 20px;
    }

    .progress-fill {
        background-color: var(--primary-blue);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    .success-fill {
        background-color: var(--success-green);
    }

    .warning-fill {
        background-color: var(--alert-orange);
    }

    h1, h2, h3 {
        color: var(--text-primary);
    }

    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--card-bg);
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        background-color: transparent;
    }

    .stTabs [aria-selected="true"] {
        color: var(--text-primary);
        background-color: var(--primary-blue);
        border-radius: 8px;
    }

    .discovery-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    .discovery-card:hover {
        border-color: var(--primary-blue);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .metric-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, var(--dark-bg) 100%);
        border: 1px solid var(--border-color);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--text-primary);
    }

    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .phase-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .phase-investigacion { background-color: #3B82F6; color: white; }
    .phase-diseno { background-color: #8B5CF6; color: white; }
    .phase-implementacion { background-color: #F59E0B; color: white; }
    .phase-evaluacion { background-color: #10B981; color: white; }
    .phase-refinamiento { background-color: #EF4444; color: white; }
</style>
""", unsafe_allow_html=True)


class DashboardManager:
    """Manager for dashboard data and state."""

    def __init__(self, data_dir: str = "dashboard_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.data_dir / "dashboard_state.json"
        self.results_dir = Path("results")

    def load_state(self) -> Dict[str, Any]:
        """Load dashboard state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return self._get_default_state()

    def _get_default_state(self) -> Dict[str, Any]:
        """Return default state structure."""
        return {
            'total_ideas': 0,
            'pending_ideas': 0,
            'processing_ideas': 0,
            'completed_ideas': 0,
            'failed_ideas': 0,
            'success_rate': 0.0,
            'ideas': {},
            'discoveries': [],
            'last_update': time.time()
        }

    def save_state(self, state: Dict[str, Any]) -> None:
        """Save dashboard state to file."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            st.error(f"Failed to save state: {e}")

    def get_worktree_data(self) -> pd.DataFrame:
        """Get worktree data for visualization."""
        state = self.load_state()
        ideas = state.get('ideas', {})

        data = []
        for idea_id, info in ideas.items():
            data.append({
                'ID': idea_id,
                'Nombre': info.get('name', 'Unknown'),
                'Estado': info.get('status', 'pendiente'),
                'Fase': info.get('current_phase', 'N/A'),
                'Iteraciones': info.get('iterations', 0),
                'Score': info.get('confidence_score', 0),
                'Tiempo (min)': round(info.get('execution_time', 0) / 60, 1),
                'Actualizado': datetime.fromtimestamp(info.get('last_update', time.time())).strftime('%Y-%m-%d %H:%M')
            })

        return pd.DataFrame(data)

    def get_discoveries(self, top_n: int = 10) -> pd.DataFrame:
        """Get top discoveries."""
        state = self.load_state()
        discoveries = state.get('discoveries', [])

        # Sort by relevance score
        discoveries = sorted(discoveries, key=lambda x: x.get('relevance_score', 0), reverse=True)[:top_n]

        data = []
        for disc in discoveries:
            data.append({
                'Fármaco': disc.get('drug_candidate', 'Unknown'),
                'Enfermedad': disc.get('target_disease', 'Unknown'),
                'Score Relevancia': disc.get('relevance_score', 0),
                'Score Confianza': disc.get('confidence_score', 0),
                'Modelo': disc.get('model_type', 'N/A'),
                'Recomendación': disc.get('recommendation', 'N/A')
            })

        return pd.DataFrame(data)

    def export_to_csv(self, df: pd.DataFrame, filename: str = "dashboard_export.csv") -> str:
        """Export DataFrame to CSV."""
        output_path = self.data_dir / filename
        df.to_csv(output_path, index=False, encoding='utf-8')
        return str(output_path)

    def export_to_pdf(self, fig, filename: str = "dashboard_report.pdf") -> str:
        """Export plot to PDF (requires kaleido)."""
        try:
            output_path = self.data_dir / filename
            fig.write_image(output_path, format='pdf', width=1200, height=800)
            return str(output_path)
        except Exception as e:
            st.warning(f"PDF export failed (install kaleido for PDF support): {e}")
            return None


@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_dashboard_data(manager: DashboardManager) -> Dict[str, Any]:
    """Load and cache dashboard data."""
    return manager.load_state()


def render_header():
    """Render dashboard header."""
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("💊 PharmaLoop Dashboard")
        st.caption("Sistema de Reposicionamiento de Fármacos")
    with col2:
        if st.button("🔄 Actualizar", type="primary"):
            st.cache_data.clear()
            st.rerun()
    with col3:
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)


def render_metrics_cards(state: Dict[str, Any]):
    """Render top-level metrics cards."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Ideas",
            value=state.get('total_ideas', 0),
            delta=None
        )

    with col2:
        st.metric(
            label="En Progreso",
            value=state.get('processing_ideas', 0),
            delta=f"{state.get('pending_ideas', 0)} pendientes"
        )

    with col3:
        st.metric(
            label="Completadas",
            value=state.get('completed_ideas', 0),
            delta=f"+{state.get('completed_ideas', 0)}"
        )

    with col4:
        st.metric(
            label="Tasa de Éxito",
            value=f"{state.get('success_rate', 0):.1f}%",
            delta=None
        )

    with col5:
        st.metric(
            label="Fallidas",
            value=state.get('failed_ideas', 0),
            delta=None
        )


def render_worktree_progress(manager: DashboardManager):
    """Render worktree progress view."""
    st.subheader("📊 Progreso de Worktrees")

    df = manager.get_worktree_data()

    if df.empty:
        st.info("No hay worktrees activos en este momento")
        return

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filtrar por Estado",
            options=df['Estado'].unique(),
            default=df['Estado'].unique()
        )
    with col2:
        phase_filter = st.multiselect(
            "Filtrar por Fase",
            options=df['Fase'].unique(),
            default=df['Fase'].unique()
        )
    with col3:
        min_score = st.slider("Score Mínimo", 0, 100, 0)

    # Apply filters
    filtered_df = df[
        (df['Estado'].isin(status_filter)) &
        (df['Fase'].isin(phase_filter)) &
        (df['Score'] >= min_score)
    ]

    # Display worktrees
    for _, row in filtered_df.iterrows():
        with st.container():
            col_a, col_b, col_c, col_d, col_e = st.columns([3, 2, 2, 2, 2])

            with col_a:
                st.write(f"**{row['Nombre']}**")
                st.caption(row['ID'])

            with col_b:
                phase = row['Fase']
                phase_class = f"phase-{phase.lower().replace(' ', '_')}" if phase != 'N/A' else ""
                st.markdown(f'<span class="phase-badge {phase_class}">{phase}</span>', unsafe_allow_html=True)

            with col_c:
                # Progress bar
                progress = min(row['Score'], 100)
                color_class = "success-fill" if progress >= 75 else ("warning-fill" if progress >= 50 else "")
                st.markdown(f"""
                    <div class="progress-bar">
                        <div class="progress-fill {color_class}" style="width: {progress}%"></div>
                    </div>
                    <small>{progress}/100</small>
                """, unsafe_allow_html=True)

            with col_d:
                st.write(f"🕒 {row['Tiempo (min)']} min")

            with col_e:
                st.write(f"🔄 {row['Iteraciones']}")


def render_advanced_charts(manager: DashboardManager):
    """Render advanced analytics charts."""
    st.subheader("📈 Análisis de Avances")

    tab1, tab2, tab3 = st.tabs(["Distribución de Scores", "Timeline", "Heatmap"])

    with tab1:
        df = manager.get_worktree_data()
        if not df.empty and 'Score' in df.columns:
            fig = px.histogram(
                df,
                x='Score',
                nbins=20,
                title='Distribución de Scores de Confianza',
                labels={'Score': 'Score de Confianza', 'count': 'Frecuencia'},
                color_discrete_sequence=['#1E3A8A']
            )
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='#0F172A',
                plot_bgcolor='#1E293B'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes")

    with tab2:
        df = manager.get_worktree_data()
        if not df.empty and 'Actualizado' in df.columns:
            # Create timeline
            timeline_data = []
            for _, row in df.iterrows():
                if row['Estado'] == 'completado':
                    timeline_data.append({
                        'Tarea': row['Nombre'],
                        'Inicio': datetime.now() - timedelta(minutes=row['Tiempo (min)']),
                        'Fin': datetime.now(),
                        'Estado': row['Estado']
                    })

            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                fig = px.timeline(
                    timeline_df,
                    x_start="Inicio",
                    x_end="Fin",
                    y="Tarea",
                    color="Estado",
                    title="Timeline de Completitud",
                    color_discrete_map={
                        'completado': '#10B981',
                        'procesando': '#F59E0B',
                        'pendiente': '#6B7280'
                    }
                )
                fig.update_layout(template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay tareas completadas aún")
        else:
            st.info("No hay datos de timeline")

    with tab3:
        # Drug vs Disease heatmap
        state = manager.load_state()
        ideas = state.get('ideas', {})

        if ideas:
            drugs = []
            diseases = []
            scores = []

            for idea_id, info in ideas.items():
                drugs.append(info.get('drug_candidate', 'Unknown'))
                diseases.append(info.get('target_disease', 'Unknown'))
                scores.append(info.get('relevance_score', 0))

            heatmap_df = pd.DataFrame({
                'Fármaco': drugs,
                'Enfermedad': diseases,
                'Score': scores
            })

            pivot = heatmap_df.pivot_table(
                values='Score',
                index='Fármaco',
                columns='Enfermedad',
                aggfunc='mean',
                fill_value=0
            )

            fig = px.imshow(
                pivot.values,
                labels=dict(x="Enfermedad", y="Fármaco", color="Score"),
                x=pivot.columns,
                y=pivot.index,
                color_continuous_scale='Viridis',
                title="Heatmap: Fármacos vs Enfermedades"
            )
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos para el heatmap")


def render_discoveries(manager: DashboardManager):
    """Render top discoveries panel."""
    st.subheader("⭐ Descubrimientos Destacados")

    df = manager.get_discoveries(top_n=10)

    if df.empty:
        st.info("Aún no hay descubrimientos destacados")
        return

    # Display as cards
    for _, row in df.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

            with col1:
                st.write(f"**{row['Fármaco']}**")
                st.caption(row['Enfermedad'])

            with col2:
                color = "#10B981" if row['Score Relevancia'] >= 70 else ("#F59E0B" if row['Score Relevancia'] >= 50 else "#EF4444")
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>{row['Score Relevancia']}/100</span>",
                           unsafe_allow_html=True)

            with col3:
                st.write(f"🎯 {row['Modelo']}")

            with col4:
                rec_color = "#10B981" if row['Recomendación'] == 'proceed' else "#F59E0B"
                st.markdown(f"<span style='color: {rec_color};'>{row['Recomendación'].upper()}</span>",
                           unsafe_allow_html=True)

            st.divider()


def render_chemical_structures():
    """Render chemical structures visualization."""
    st.subheader("🧪 Estructuras Químicas")

    # This would integrate with RDKit for 2D rendering
    st.info("💡 Las estructuras químicas se generan a partir de datos ChEMBL/ChEBI")

    # Placeholder for RDKit integration
    smiles_examples = {
        "Metformina": "CN(C)C(=O)N(C)C",
        "Aspirina": "CC(=O)Oc1ccccc1C(=O)O",
        "Rapamicina": "C1C=C(C2=CC=CC=C2)C(=O)C3=CC=CC=C3"
    }

    col1, col2, col3 = st.columns(3)
    for col, (drug, smiles) in zip([col1, col2, col3], smiles_examples.items()):
        with col:
            st.write(f"**{drug}**")
            st.code(smiles, language="python")
            if st.button(f"Ver en PubChem", key=f"pubchem_{drug}"):
                st.markdown(f"[Abrir PubChem](https://pubchem.ncbi.nlm.nih.gov/#query={smiles})")


def render_literature_links():
    """Render literature links panel."""
    st.subheader("📚 Literatura Científica")

    st.write("- **PubMed**: Búsqueda de artículos relacionados")
    st.write("- **ChEMBL**: Datos de bioactividad")
    st.write("- **PDB**: Estructuras proteicas")
    st.write("- **DrugBank**: Información de fármacos")

    query = st.text_input("Buscar en PubMed:", placeholder="metformin cancer AMPK")
    if query:
        st.markdown(f"[🔍 Ver resultados en PubMed](https://pubmed.ncbi.nlm.nih.gov/?term={query.replace(' ', '+')})")


def render_export_options(manager: DashboardManager):
    """Render export options."""
    st.subheader("📥 Exportar Reportes")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Exportar CSV"):
            df = manager.get_worktree_data()
            csv_path = manager.export_to_csv(df)
            with open(csv_path, 'rb') as f:
                st.download_button(
                    label="📥 Descargar CSV",
                    data=f,
                    file_name="dashboard_export.csv",
                    mime="text/csv"
                )

    with col2:
        if st.button("📑 Exportar PDF"):
            df = manager.get_worktree_data()
            fig = px.bar(df, x='Nombre', y='Score', title='Reporte de Scores')
            pdf_path = manager.export_to_pdf(fig)
            if pdf_path:
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="📥 Descargar PDF",
                        data=f,
                        file_name="dashboard_report.pdf",
                        mime="application/pdf"
                    )

    with col3:
        if st.button("💾 Guardar Estado"):
            state = manager.load_state()
            manager.save_state(state)
            st.success("Estado guardado")


def render_sidebar(manager: DashboardManager):
    """Render sidebar with filters and info."""
    with st.sidebar:
        st.header("⚙️ Configuración")

        st.subheader("Filtros")
        state = manager.load_state()

        # Date range filter
        st.write("**Rango de Fechas**")
        date_range = st.date_input(
            "Seleccionar rango",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            max_value=datetime.now()
        )

        # Status filter
        status_options = ['pendiente', 'procesando', 'completado', 'error', 'interrumpido']
        selected_status = st.multiselect(
            "Estados",
            options=status_options,
            default=status_options
        )

        # Score range
        score_range = st.slider(
            "Rango de Score",
            min_value=0,
            max_value=100,
            value=(0, 100)
        )

        st.divider()

        st.subheader("📊 Estadísticas")
        ideas = state.get('ideas', {})

        if ideas:
            total = len(ideas)
            completed = sum(1 for i in ideas.values() if i.get('status') == 'completado')
            avg_score = np.mean([i.get('relevance_score', 0) for i in ideas.values()])

            st.metric("Total Ideas", total)
            st.metric("Completadas", completed)
            st.metric("Score Promedio", f"{avg_score:.1f}")

        st.divider()
        st.caption("🔄 Última actualización:")
        st.caption(datetime.fromtimestamp(state.get('last_update', time.time())).strftime('%Y-%m-%d %H:%M:%S'))


def main():
    """Main dashboard application."""
    # Initialize manager
    manager = DashboardManager()

    # Load state
    state = load_dashboard_data(manager)

    # Update last refresh time
    current_time = time.time()
    last_update = state.get('last_update', current_time)

    # Check for auto-refresh
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False, key="autorefresh_main")

    if auto_refresh:
        time_elapsed = current_time - last_update
        if time_elapsed >= 30:
            st.cache_data.clear()
            st.rerun()

    # Render components
    render_header()
    render_metrics_cards(state)

    st.divider()

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Progreso",
        "📈 Análisis",
        "⭐ Descubrimientos",
        "⚗️ Química"
    ])

    with tab1:
        render_worktree_progress(manager)

    with tab2:
        render_advanced_charts(manager)

    with tab3:
        render_discoveries(manager)

    with tab4:
        render_chemical_structures()
        render_literature_links()

    st.divider()

    # Export options
    render_export_options(manager)

    # Footer
    st.markdown("---")
    st.caption("PharmaLoop v1.0 | Dashboard generado automáticamente")


if __name__ == "__main__":
    main()