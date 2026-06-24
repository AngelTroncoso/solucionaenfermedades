"""Design view component for dashboard."""

import streamlit as st
from typing import Dict, Any, List
from loguru import logger


class DesignView:
    """Component for displaying design phase results."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def render(self, design_data: Dict[str, Any]) -> None:
        """Render design view."""
        st.header("🧬 Design Phase")
        
        tab1, tab2, tab3 = st.tabs(["Candidates", "Properties", "Synthesis"])
        
        with tab1:
            self._render_candidates(design_data)
        
        with tab2:
            self._render_properties(design_data)
        
        with tab3:
            self._render_synthesis(design_data)

    def _render_candidates(self, design_data: Dict[str, Any]) -> None:
        """Render candidate molecules."""
        st.subheader("Candidate Molecules")
        
        candidates = design_data.get("candidates", [])
        if candidates:
            st.write(f"Generated {len(candidates)} candidates")
            
            for idx, candidate in enumerate(candidates[:10]):
                with st.expander(f"Candidate {idx + 1}: {candidate.get('smiles', 'N/A')[:50]}..."):
                    st.json(candidate)
        else:
            st.info("No candidates generated yet")

    def _render_properties(self, design_data: Dict[str, Any]) -> None:
        """Render molecular properties."""
        st.subheader("Molecular Properties")
        
        properties = design_data.get("properties", {})
        if properties:
            st.json(properties)
        else:
            st.info("No properties calculated yet")

    def _render_synthesis(self, design_data: Dict[str, Any]) -> None:
        """Render synthesis routes."""
        st.subheader("Synthesis Routes")
        
        routes = design_data.get("synthesis_routes", [])
        if routes:
            for idx, route in enumerate(routes):
                with st.expander(f"Route {idx + 1}"):
                    st.json(route)
        else:
            st.info("No synthesis routes proposed yet")