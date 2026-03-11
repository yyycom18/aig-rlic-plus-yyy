"""
Indicator DNA cards — metadata loader and helpers.

This module reads:
- data/indicator_dna_cards.json  (human-readable card content)
- data/indicator_mapping.json    (primary_DNA, secondary_DNA, rationale, confidence)

and exposes a small dataclass + loader used by the Streamlit UI
and by validation / API endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional
import json
import os


@dataclass
class IndicatorDNACard:
    """
    Full Indicator DNA card as displayed in the UI.

    Core textual fields (from indicator_dna_cards.json):
    - indicator_name: Human-readable name of the indicator
    - identity_type: High-level identity bucket (e.g., Growth, Risk & Volatility)
    - primary_use_case: Main use case (chip)
    - secondary_use_case: Secondary use case (chip)
    - description: One-line description (prominent text)
    - why_classified: Short rationale (goes into the expander)
    - last_updated: ISO date string for last edit
    - author: Author / analyst responsible for the classification

    Classification metadata (from indicator_mapping.json):
    - primary_DNA: Primary DNA category
    - secondary_DNA: List of secondary DNA categories
    - rationale: Short rationale for DNA assignment
    - confidence: Confidence level string (e.g., High / Medium / Low)

    Optional metadata (reserved for future extensions):
    - data_frequency: e.g. daily / weekly / monthly / low-frequency
    - canonical_source_path: Path to primary source file, if available
    """

    indicator_name: str
    identity_type: str
    primary_use_case: str
    secondary_use_case: str
    description: str
    why_classified: str
    last_updated: str
    author: str

    primary_DNA: Optional[str] = None
    secondary_DNA: List[str] = field(default_factory=list)
    rationale: Optional[str] = None
    confidence: Optional[str] = None

    data_frequency: Optional[str] = None
    canonical_source_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize card to a plain dict suitable for JSON export."""
        return asdict(self)


class IndicatorDNACardLoader:
    """
    Loader for IndicatorDNACard objects.

    - cards_path: JSON list of card dictionaries (indicator_dna_cards.json)
    - mapping_path: JSON list of mapping dictionaries (indicator_mapping.json)

    The loader merges both sources on indicator_name. Mapping fields override
    any overlapping keys from the cards file, except for indicator_name itself.
    """

    def __init__(self, cards_path: str, mapping_path: Optional[str] = None) -> None:
        self.cards_path = cards_path
        self.mapping_path = mapping_path
        self._cache: Dict[str, IndicatorDNACard] = {}

    def load(self) -> Dict[str, IndicatorDNACard]:
        """Load all cards into memory and return mapping keyed by indicator_name."""
        cards_raw = self._load_cards()
        mapping_raw = self._load_mapping() if self.mapping_path else []
        mapping_index: Dict[str, Dict[str, Any]] = {
            m["indicator_name"]: m for m in mapping_raw if m.get("indicator_name")
        }

        result: Dict[str, IndicatorDNACard] = {}
        for entry in cards_raw:
            name = entry.get("indicator_name")
            if not name:
                continue
            mapping_extra = mapping_index.get(name, {})
            # Merge mapping fields, excluding indicator_name (we keep the card's name)
            merged: Dict[str, Any] = dict(entry)
            for key, value in mapping_extra.items():
                if key == "indicator_name":
                    continue
                merged[key] = value

            # Normalize secondary_DNA to list
            secondary_dna = merged.get("secondary_DNA")
            if isinstance(secondary_dna, str):
                merged["secondary_DNA"] = [secondary_dna]

            result[name] = IndicatorDNACard(**merged)

        self._cache = result
        return result

    def _load_cards(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.cards_path):
            raise FileNotFoundError(f"indicator_dna_cards.json not found: {self.cards_path}")
        with open(self.cards_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("indicator_dna_cards.json must contain a JSON list")
        return data

    def _load_mapping(self) -> List[Dict[str, Any]]:
        if not self.mapping_path:
            return []
        if not os.path.exists(self.mapping_path):
            raise FileNotFoundError(f"indicator_mapping.json not found: {self.mapping_path}")
        with open(self.mapping_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("indicator_mapping.json must contain a JSON list")
        return data

    def get_all(self) -> Dict[str, IndicatorDNACard]:
        """Return cached cards, loading from disk if necessary."""
        if not self._cache:
            return self.load()
        return self._cache.copy()

    def get(self, indicator_name: str) -> Optional[IndicatorDNACard]:
        """Retrieve a single card by indicator_name."""
        if not self._cache:
            self.load()
        return self._cache.get(indicator_name)

