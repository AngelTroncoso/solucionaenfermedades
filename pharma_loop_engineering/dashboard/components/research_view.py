"""Research view component for dashboard."""

import streamlit as st
from typing import Dict, Any, List
from loguru import logger


class ResearchView:
    """Component for displaying research phase data."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def render(self, research_data: Dict[str, Any]) -> None:
        """Render research view."""
        st.header("🔬 Research Phase")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Literature Search")
            if research_data.get("literature"):
                st.write(f"Found {len(research_data['literature'])} articles")
                for article in research_data["literature"][:5]:
                    with st.expander(article.get("title", "Untitled")):
                        st.write(f"**Authors:** {article.get('authors', 'N/A')}")
                        st.write(f"**Journal:** {article.get('journal', 'N/A')}")
                        st.write(f"**Year:** {article.get('year', 'N/A')}")
            else:
                st.info("No literature data available")
        
        with col2:
            st.subheader("Database Results")
            if research_data.get("databases"):
                st.write(f"Found {len(research_data['databases'])} compounds")
            else:
                st.info("No database results available")

    def search_interface(self) -> str:
        """Render search interface."""
        query = st.text_input("Enter search query", key="research_query")
        db_choice = st.selectbox(
            "Database",
            ["PubMed", "ChEMBL", "Patents", "All"]
        )
        return query