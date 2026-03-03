"""Global sidebar navigation and filters."""

import streamlit as st


def render_sidebar():
    """Render the global sidebar with navigation and info."""
    with st.sidebar:
        st.markdown("## AIG-RLIC+")
        st.markdown("*Credit Market Signals for Equity Investors*")

        st.markdown("---")

        st.markdown("### Findings")
        st.page_link("app.py", label="Executive Summary", icon="🏠")
        st.page_link("pages/1_hy_ig_story.py", label="1. The Story", icon="📖")
        st.page_link("pages/2_hy_ig_evidence.py", label="2. The Evidence", icon="🔬")
        st.page_link("pages/3_hy_ig_strategy.py", label="3. The Strategy", icon="🎯")
        st.page_link("pages/4_hy_ig_methodology.py", label="4. Methodology", icon="📐")

        st.markdown("---")

        st.markdown(
            '<p style="font-size: 0.8rem; color: #999;">'
            "Data through 2025-12-31<br>"
            "OOS window: 2018-2025"
            "</p>",
            unsafe_allow_html=True,
        )
