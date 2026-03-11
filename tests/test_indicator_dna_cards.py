from __future__ import annotations

from pathlib import Path

from app.core.indicator_dna_cards import IndicatorDNACardLoader, IndicatorDNACard
from scripts.validate_dna import validate_indicator_dna


def test_indicator_dna_card_loader_merges_mapping(tmp_path):
    # Prepare minimal cards + mapping
    cards = [
        {
            "indicator_name": "Test Indicator",
            "identity_type": "Growth",
            "primary_use_case": "Test primary",
            "secondary_use_case": "Test secondary",
            "description": "One-line description.",
            "why_classified": "Short rationale.",
            "last_updated": "2026-03-08",
            "author": "Tester",
        }
    ]
    mapping = [
        {
            "indicator_name": "Test Indicator",
            "primary_DNA": "Growth",
            "secondary_DNA": ["Inflation/Prices"],
            "rationale": "DNA rationale",
            "confidence": "High",
        }
    ]

    cards_path = tmp_path / "indicator_dna_cards.json"
    mapping_path = tmp_path / "indicator_mapping.json"
    cards_path.write_text(__import__("json").dumps(cards), encoding="utf-8")
    mapping_path.write_text(__import__("json").dumps(mapping), encoding="utf-8")

    loader = IndicatorDNACardLoader(str(cards_path), str(mapping_path))
    mapping_out = loader.load()
    assert "Test Indicator" in mapping_out
    card: IndicatorDNACard = mapping_out["Test Indicator"]
    assert card.primary_DNA == "Growth"
    assert card.secondary_DNA == ["Inflation/Prices"]
    assert card.confidence == "High"
    assert card.rationale == "DNA rationale"


def test_validate_indicator_dna_schema(tmp_path):
    # Use the same minimal files as above to test validator
    cards = [
        {
            "indicator_name": "Test Indicator",
            "identity_type": "Growth",
            "primary_use_case": "Test primary",
            "secondary_use_case": "Test secondary",
            "description": "One-line description.",
            "why_classified": "Short rationale.",
            "last_updated": "2026-03-08",
            "author": "Tester",
        }
    ]
    mapping = [
        {
            "indicator_name": "Test Indicator",
            "primary_DNA": "Growth",
            "secondary_DNA": ["Inflation/Prices"],
            "rationale": "DNA rationale",
            "confidence": "High",
        }
    ]
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "indicator_dna_cards.json").write_text(
        __import__("json").dumps(cards), encoding="utf-8"
    )
    (data_dir / "indicator_mapping.json").write_text(
        __import__("json").dumps(mapping), encoding="utf-8"
    )

    errors = validate_indicator_dna(base_dir=tmp_path)
    assert errors == []

