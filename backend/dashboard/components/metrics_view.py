"""Metrics view component for dashboard."""

import streamlit as st
from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from loguru import logger


class MetricsView:
    """Component for displaying metrics and KPIs."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def render(self, evaluation_data: Dict[str, Any]) -> None:
        """Render metrics view."""
        st.header("📈 Metrics & KPIs")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._metric_card("Molecules", "0", "↑ 0")
        with col2:
            self._metric_card("Success Rate", "0%", "↑ 0%")
        with col3:
            self._metric_card("Avg. Score", "0.0", "↑ 0.0")
        with col4:
            self._metric_card("Iterations", "0", "↑ 0")
        
        st.divider()
        
        # Graphs
        tab1, tab2 = st.tabs(["Performance", "Trends"])
        
        with tab1:
            self._render_performance_charts(evaluation_data)
        
        with tab2:
            self._render_trends(evaluation_data)

    def _metric_card(self, label: str, value: str, delta: str) -> None:
        """Render a metric card."""
        st.metric(label=label, value=value, delta=delta)

    def _render_performance_charts(self, evaluation_data: Dict[str, Any]) -> None:
        """Render performance charts."""
        st.subheader("Performance Metrics")
        
        metrics = evaluation_data.get("metrics", {})
        if metrics:
            df = pd.DataFrame([metrics])
            st.bar_chart(df)
        else:
            st.info("No metrics available")

    def _render_trends(self, evaluation_data: Dict[str, Any]) -> None:
        """Render trend charts."""
        st.subheader("Trend Analysis")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=[1, 2, 3], mode='lines', name='Example'))
        st.plotly_chart(fig, use_container_width=True)