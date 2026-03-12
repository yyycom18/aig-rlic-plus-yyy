from __future__ import annotations

from pathlib import Path

import types

from app.components import dna_card
from app.core.indicator_dna_cards import IndicatorDNACard


def test_append_edit_log_creates_file(tmp_path, monkeypatch):
    # Redirect project root used inside dna_card module to tmp_path
    # by patching os.path.dirname(__file__) logic via environment
    # We simulate by temporarily changing __file__ resolution.
    original_file = dna_card.__file__
    try:
        dna_card.__file__ = str(tmp_path / "app" / "components" / "dna_card.py")
        (tmp_path / "results").mkdir(parents=True, exist_ok=True)

        # Call the private helper
        dna_card._append_edit_log(
            indicator_name="Test Indicator",
            admin="Tester",
            field="confidence",
            before="Medium",
            after="High",
        )
        log_path = tmp_path / "results" / "indicator_dna_metadata_log.csv"
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8").strip().splitlines()
        # header + one line
        assert len(content) == 2
        assert "Test Indicator" in content[1]
        assert "Tester" in content[1]
    finally:
        dna_card.__file__ = original_file


def test_render_dna_card_smoke_and_author_hidden(monkeypatch):
    """Smoke test: render_dna_card callable and does not surface author."""

    # Patch streamlit functions used in dna_card with a stub that records text
    class DummySt:
        def __init__(self):
            self.texts = []

        def subheader(self, text, **kwargs):
            self.texts.append(str(text))

        def markdown(self, text, **kwargs):
            self.texts.append(str(text))

        def caption(self, text, **kwargs):
            self.texts.append(str(text))

        def expander(self, *args, **kwargs):
            class Ctx:
                def __enter__(self_inner):
                    return None

                def __exit__(self_inner, exc_type, exc, tb):
                    return False

            return Ctx()

        def text_input(self, *args, **kwargs):
            return "Tester"

        def selectbox(self, *args, **kwargs):
            return "High"

        def text_area(self, *args, **kwargs):
            return "Updated rationale"

        def button(self, *args, **kwargs):
            # record the button label for assertions
            if args:
                self.texts.append(str(args[0]))
            return False

        @property
        def session_state(self):  # not used directly in this test
            return {}

    dummy = DummySt()
    monkeypatch.setattr(dna_card, "st", dummy)

    card = IndicatorDNACard(
        indicator_name="Test Indicator",
        identity_type="Growth",
        primary_use_case="Test primary",
        secondary_use_case="Test secondary",
        description="Description",
        why_classified="Why",
        last_updated="2026-03-08",
        author="Tester",
        primary_DNA="Growth",
        secondary_DNA=["Inflation/Prices"],
        rationale="Rationale",
        confidence="High",
    )

    dna_card.render_dna_card(card, admin_enabled=False)

    # Ensure author value does not appear in any rendered text
    joined = " ".join(dummy.texts)
    assert "Tester" not in joined
    # Ensure badge text includes "Confidence: High"
    assert "Confidence: High" in joined

