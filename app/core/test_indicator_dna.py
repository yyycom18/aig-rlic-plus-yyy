from datetime import datetime

import pytest

from .indicator_dna import IndicatorDNA, IndicatorDNALoader


def test_indicator_dna_from_dict_roundtrip():
    """Test dict → IndicatorDNA → dict (ISO as_of) conversion."""
    data = {
        "id": "test",
        "name": "Test Indicator",
        "identity_type": "Risk Overlay",
        "primary_use_case": "Test primary",
        "secondary_use_case": "Test secondary",
        "one_line_summary": "Test summary",
        "as_of": "2026-02-28",
    }
    dna = IndicatorDNA.from_dict(data)
    assert dna.id == "test"
    assert isinstance(dna.as_of, datetime)

    out = dna.to_dict()
    assert out["id"] == "test"
    assert isinstance(out["as_of"], str)
    assert out["as_of"].startswith("2026-02-28")


def test_indicator_dna_missing_fields_raises():
    """Missing required fields should raise ValueError."""
    incomplete = {
        "id": "x",
        "name": "X",
        # identity_type missing
        "primary_use_case": "P",
        "secondary_use_case": "S",
        "one_line_summary": "Summary",
        "as_of": "2026-02-28",
    }
    with pytest.raises(ValueError):
        IndicatorDNA.from_dict(incomplete)


def test_override_precedence(tmp_path, monkeypatch):
    """Test override > CSV > JSON precedence for IndicatorDNALoader."""
    # Create temporary JSON config
    json_path = tmp_path / "indicator_dna.json"
    base_cfg = {
        "indicators": [
            {
                "id": "base_id",
                "name": "Base Name",
                "identity_type": "Risk Overlay",
                "primary_use_case": "Base primary",
                "secondary_use_case": "Base secondary",
                "one_line_summary": "Base summary",
                "as_of": "2026-02-28",
            }
        ]
    }
    json_path.write_text(__import__("json").dumps(base_cfg), encoding="utf-8")

    # Create CSV override
    csv_path = tmp_path / "indicator_dna.csv"
    csv_path.write_text(
        "id,name,identity_type,primary_use_case,secondary_use_case,one_line_summary,as_of\n"
        "base_id,CSV Name,CSV Type,CSV primary,CSV secondary,CSV summary,2026-03-01\n",
        encoding="utf-8",
    )

    loader = IndicatorDNALoader(json_path=str(json_path))
    # Load with CSV only – should override JSON
    mapping = loader.load(csv_path=str(csv_path))
    dna = mapping["base_id"]
    assert dna.name == "CSV Name"
    assert dna.identity_type == "CSV Type"
    assert dna.as_of == datetime.fromisoformat("2026-03-01")

    # Now apply explicit override (highest priority)
    override = {
        "base_id": {
            "id": "base_id",
            "name": "Override Name",
            "identity_type": "Override Type",
            "primary_use_case": "Override primary",
            "secondary_use_case": "Override secondary",
            "one_line_summary": "Override summary",
            "as_of": "2026-03-15",
        }
    }
    mapping2 = loader.load(csv_path=str(csv_path), override_dict=override)
    dna2 = mapping2["base_id"]
    assert dna2.name == "Override Name"
    assert dna2.identity_type == "Override Type"
    assert dna2.as_of == datetime.fromisoformat("2026-03-15")

