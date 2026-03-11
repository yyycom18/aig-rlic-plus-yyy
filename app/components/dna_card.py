"""Streamlit Indicator DNA card component.

Renders a compact card with:
- identity / use-case chips
- bold one-line description
- expandable "Why this classification"
- confidence badge and metadata
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime
import os

import streamlit as st

from core import IndicatorDNACard


_CONFIDENCE_COLORS = {
    "High": "#16a34a",   # green
    "Medium": "#facc15", # amber
    "Low": "#f97316",    # orange
}

# Primary DNA chip colors (macro classes) — light backgrounds for good contrast
_PRIMARY_DNA_COLORS = {
    "Growth": "#dbeafe",
    "Inflation/Prices": "#fef9c3",
    "Risk & Volatility": "#fee2e2",
    "Credit & Financial Stress": "#e0f2fe",
    "Liquidity & Monetary": "#ede9fe",
    "Sector/Housing": "#dcfce7",
    "Sector/Commodity/Structural": "#f1f5f9",
}


def _chip(label: str, color: str = "#e5e7eb") -> None:
    """Render a small pill-shaped chip."""
    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:2px 8px;
            margin-right:6px;
            border-radius:999px;
            background-color:{color};
            font-size:0.78rem;
        ">{label}</span>
        """,
        unsafe_allow_html=True,
    )


def _append_edit_log(
    indicator_name: str,
    admin: str,
    field: str,
    before: Optional[str],
    after: Optional[str],
) -> None:
    """Append a single-field edit event to results/indicator_dna_metadata_log.csv."""
    root_dir = os.path.dirname(os.path.dirname(__file__))  # app/ → project root
    log_path = os.path.join(root_dir, "results", "indicator_dna_metadata_log.csv")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    is_new = not os.path.exists(log_path)
    ts = datetime.utcnow().isoformat(timespec="seconds")
    line = f"{ts},{indicator_name},{admin},{field},{before or ''},{after or ''}\n"
    if is_new:
        header = "timestamp,indicator_name,admin,field,before,after\n"
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write(line)
    else:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)


def render_dna_card(card: IndicatorDNACard, admin_enabled: bool = True) -> None:
    """Render a single IndicatorDNACard in a clean, compact layout."""
    # Centered, max-width container for improved readability
    st.markdown(
        '<div style="max-width:900px;margin-left:auto;margin-right:auto;padding:8px 12px;">',
        unsafe_allow_html=True,
    )

    # Header row: title (left) and confidence badge (right), grouped and compact
    header_col, header_conf = st.columns([8, 1])
    with header_col:
        st.subheader(card.indicator_name)
    with header_conf:
        if card.confidence:
            color = _CONFIDENCE_COLORS.get(card.confidence, "#e5e7eb")
            st.markdown(
                f"""
                <div style="text-align:right;">
                    <span style="
                        display:inline-block;
                        padding:4px 10px;
                        border-radius:999px;
                        background-color:{color};
                        font-size:0.85rem;
                        font-weight:600;
                    ">
                        {card.confidence}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Grouped chips and use-case layout (two-column for compactness)
    st.markdown(
        "<div style='display:flex;flex-wrap:wrap;gap:6px;align-items:center;'>",
        unsafe_allow_html=True,
    )
    # Identity (DNA) chip
    primary_label = card.primary_DNA or card.identity_type
    primary_color = _PRIMARY_DNA_COLORS.get(primary_label, "#e5e7eb")
    _chip(primary_label, primary_color)
    # Use-case chips are placed next
    _chip(card.primary_use_case, "#ecfdf3")
    _chip(card.secondary_use_case, "#fefce8")
    st.markdown("</div>", unsafe_allow_html=True)

    # One-line description (keep centered container)
    st.markdown(f"**{card.description}**")

    # Optional DNA classification (primary + secondary) displayed succinctly
    if card.primary_DNA or card.secondary_DNA:
        cols = st.columns([1, 1])
        with cols[0]:
            if card.primary_DNA:
                st.markdown(f"**Primary DNA:** {card.primary_DNA}")
        with cols[1]:
            if card.secondary_DNA:
                st.markdown(f"**Secondary DNA:** {', '.join(card.secondary_DNA)}")

    # Expandable rationale (condensed)
    with st.expander("Why this classification", expanded=False):
        st.markdown(card.why_classified)
        if card.rationale and card.rationale != card.why_classified:
            st.markdown(f"**DNA rationale:** {card.rationale}")

    # Metadata line (last updated, optional frequency/source). Date only.
    # Ensure last_updated shows only date portion if datetime-like string provided
    last_date = str(card.last_updated).split("T")[0]
    meta_bits = [f"Last updated: {last_date}"]
    if card.data_frequency:
        meta_bits.append(f"Data frequency: {card.data_frequency}")
    if card.canonical_source_path:
        root_dir = os.path.dirname(os.path.dirname(__file__))
        abs_path = os.path.join(root_dir, card.canonical_source_path)
        exists = os.path.exists(abs_path)
        link_label = card.canonical_source_path
        # Render canonical source as a simple markdown link; if file is missing, annotate
        if exists:
            source_md = f"[{link_label}]({card.canonical_source_path})"
        else:
            source_md = f"`{link_label} (missing)`"
        meta_bits.append(f"Source: {source_md}")
    st.caption(" — ".join(meta_bits))

    # Documentation link (handoff copy) for all cards
    doc_rel_path = "handoffs/indicator_dna_ui_copy.md"
    st.caption(f"Documentation: `{doc_rel_path}`")

    # Admin edit modal (guarded)
    if not admin_enabled:
        return

    with st.expander("Admin: edit DNA metadata", expanded=False):
        st.markdown(
            "Use this panel to propose edits to the rationale / confidence. "
            "Edits are logged for review and do not overwrite the canonical JSON."
        )
        admin_name = st.text_input("Your name (for audit log)", key=f"dna_admin_name_{card.indicator_name}")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_conf = st.selectbox(
                "Confidence",
                options=["", "High", "Medium", "Low"],
                index=["", "High", "Medium", "Low"].index(card.confidence) if card.confidence in ["High", "Medium", "Low"] else 0,
                key=f"dna_conf_{card.indicator_name}",
            )
        with col2:
            new_last = st.text_input(
                "Last updated (ISO date)",
                value=card.last_updated,
                key=f"dna_last_{card.indicator_name}",
            )
        with col3:
            st.write("")  # spacer
        new_why = st.text_area(
            "Why this classification (short rationale)",
            value=card.why_classified,
            key=f"dna_why_{card.indicator_name}",
            height=100,
        )

        submitted = st.button("Save proposed edit", key=f"dna_save_{card.indicator_name}")
        if submitted:
            if not admin_name.strip():
                st.error("Admin name is required for audit logging.")
                return

            # Log changes (field-by-field)
            if new_conf and new_conf != card.confidence:
                _append_edit_log(card.indicator_name, admin_name, "confidence", card.confidence, new_conf)
                card.confidence = new_conf
            if new_last != card.last_updated:
                _append_edit_log(card.indicator_name, admin_name, "last_updated", card.last_updated, new_last)
                card.last_updated = new_last
            if new_why != card.why_classified:
                _append_edit_log(card.indicator_name, admin_name, "why_classified", card.why_classified, new_why)
                card.why_classified = new_why

            # Remember overrides in session_state so they persist for this session
            overrides: Dict[str, Any] = st.session_state.get("dna_card_overrides", {})
            overrides[card.indicator_name] = {
                "confidence": card.confidence,
                "last_updated": card.last_updated,
                "why_classified": card.why_classified,
            }
            st.session_state["dna_card_overrides"] = overrides
            st.success("Edit logged. Changes will be visible for this session and recorded for review.")

