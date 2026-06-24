"""Results view component for dashboard."""

import streamlit as st
from typing import Dict, Any, List
from loguru import logger


class ResultsView:
    """Component for displaying workflow results."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def render(self, results: Dict[str, Any]) -> None:
        """Render results view."""
        st.header("📊 Workflow Results")
        
        # Status overview
        self._render_status(results)
        
        # Detailed results by phase
        st.divider()
        
        tab1, tab2, tab3 = st.tabs(["Research", "Design", "Evaluation"])
        
        with tab1:
            st.subheader("Research Results")
            research = results.get("research", {})
            if research:
                st.json(research)
            else:
                st.info("No research results available")
        
        with tab2:
            st.subheader("Design Results")
            design = results.get("design", {})
            if design:
                st.json(design)
            else:
                st.info("No design results available")
        
        with tab3:
            st.subheader("Evaluation Results")
            evaluation = results.get("evaluation", {})
            if evaluation:
                st.json(evaluation)
            else:
                st.info("No evaluation results available")

    def _render_status(self, results: Dict[str, Any]) -> None:
        """Render workflow status."""
        phases = ["research", "design", "implementation", "evaluation", "refined"]
        
        cols = st.columns(len(phases))
        for col, phase in zip(cols, phases):
            with col:
                if phase in results:
                    st.success(f"✅ {phase.title()}")
                else:
                    st.warning(f"⏳ {phase.title()}")