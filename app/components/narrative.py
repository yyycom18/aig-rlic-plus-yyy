"""Markdown rendering with glossary tooltips and expander parsing."""

import re

import streamlit as st

from .glossary import GLOSSARY


def render_narrative(text: str):
    """Render narrative markdown, converting expander blocks to st.expander components.

    Parses <!-- expander: Title --> ... <!-- /expander --> blocks.
    """
    # Split on expander markers
    pattern = r"<!--\s*expander:\s*(.+?)\s*-->(.*?)<!--\s*/expander\s*-->"
    parts = re.split(pattern, text, flags=re.DOTALL)

    i = 0
    while i < len(parts):
        if i + 2 < len(parts) and (i % 3 == 1):
            # This is an expander title, next is content
            title = parts[i].strip()
            content = parts[i + 1].strip()
            with st.expander(title):
                st.markdown(content)
            i += 2
        else:
            # Regular markdown content
            content = parts[i].strip()
            if content:
                st.markdown(
                    f'<div class="narrative-block">{_md_to_html_simple(content)}</div>',
                    unsafe_allow_html=True,
                )
            i += 1


def _md_to_html_simple(md_text: str) -> str:
    """Minimal pass-through: let Streamlit handle full markdown rendering."""
    return md_text


def render_transition(text: str):
    """Render a transition text block between sections."""
    st.markdown(f'<div class="transition-text">{text}</div>', unsafe_allow_html=True)


def render_glossary_sidebar():
    """Render the glossary in the sidebar as expandable terms."""
    with st.sidebar:
        with st.expander("Glossary"):
            for term, definition in sorted(GLOSSARY.items()):
                st.markdown(f"**{term}:** {definition}")
