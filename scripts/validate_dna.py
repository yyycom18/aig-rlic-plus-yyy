"""
Validate Indicator DNA configuration files.

Checks:
- data/indicator_dna_cards.json schema
- data/indicator_mapping.json schema
- Cross-consistency between the two
- Optional: canonical_source_path existence when present

Usage (from project root):
    python -m scripts.validate_dna
or:
    python scripts/validate_dna.py
"""

from __future__ import annotations

from typing import List, Dict, Any, Set
from datetime import datetime
from pathlib import Path
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_indicator_dna(base_dir: Path | None = None) -> List[str]:
    """Return a list of validation error messages (empty list means OK)."""
    root = base_dir or PROJECT_ROOT
    data_dir = root / "data"

    errors: List[str] = []

    cards_path = data_dir / "indicator_dna_cards.json"
    mapping_path = data_dir / "indicator_mapping.json"

    # --- Cards file ---
    try:
        cards = _load_json(cards_path)
    except FileNotFoundError:
        return [f"Missing file: {cards_path}"]
    except Exception as exc:  # pragma: no cover - defensive
        return [f"Failed to read {cards_path}: {exc}"]

    if not isinstance(cards, list):
        errors.append("indicator_dna_cards.json must contain a JSON list.")
        return errors

    required_card_fields = {
        "indicator_name",
        "identity_type",
        "primary_use_case",
        "secondary_use_case",
        "description",
        "why_classified",
        "last_updated",
        "author",
    }
    card_names: Set[str] = set()

    for idx, card in enumerate(cards):
        if not isinstance(card, dict):
            errors.append(f"Card at index {idx} is not an object.")
            continue
        missing = required_card_fields - card.keys()
        if missing:
            errors.append(f"Card {card.get('indicator_name', idx)} missing fields: {sorted(missing)}")
        name = card.get("indicator_name")
        if isinstance(name, str) and name.strip():
            card_names.add(name)
        else:
            errors.append(f"Card at index {idx} has invalid indicator_name: {name!r}")
        # last_updated must be ISO date string
        lu = card.get("last_updated")
        try:
            datetime.fromisoformat(str(lu))
        except Exception:
            errors.append(f"Card {name} has invalid last_updated (expected ISO): {lu!r}")

    # --- Mapping file ---
    try:
        mapping = _load_json(mapping_path)
    except FileNotFoundError:
        errors.append(f"Missing file: {mapping_path}")
        return errors
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"Failed to read {mapping_path}: {exc}")
        return errors

    if not isinstance(mapping, list):
        errors.append("indicator_mapping.json must contain a JSON list.")
        return errors

    allowed_conf = {"Low", "Medium", "High"}
    for entry in mapping:
        if not isinstance(entry, dict):
            errors.append("Mapping entry is not an object.")
            continue
        name = entry.get("indicator_name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"Mapping entry has invalid indicator_name: {name!r}")
            continue
        if name not in card_names:
            errors.append(
                f"Mapping entry for indicator_name={name!r} has no matching card in indicator_dna_cards.json"
            )
        # basic field presence/type checks
        if not isinstance(entry.get("primary_DNA"), str) or not entry["primary_DNA"]:
            errors.append(f"{name}: primary_DNA must be a non-empty string.")
        sec = entry.get("secondary_DNA")
        if not isinstance(sec, list) or not all(isinstance(x, str) for x in sec):
            errors.append(f"{name}: secondary_DNA must be a list[str].")
        if not isinstance(entry.get("rationale"), str) or not entry["rationale"]:
            errors.append(f"{name}: rationale must be a non-empty string.")
        conf = entry.get("confidence")
        if conf not in allowed_conf:
            errors.append(f"{name}: confidence must be one of {sorted(allowed_conf)}, got {conf!r}.")

    # --- Optional canonical_source_path existence (if present on cards) ---
    for card in cards:
        csp = card.get("canonical_source_path")
        if not csp:
            continue
        csp_path = root / csp
        if not csp_path.exists():
            errors.append(
                f"{card.get('indicator_name')}: canonical_source_path does not exist on disk: {csp_path}"
            )

    return errors


def main() -> None:
    errors = validate_indicator_dna()
    if errors:
        print("Indicator DNA validation FAILED:")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)
    print("Indicator DNA validation PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()

