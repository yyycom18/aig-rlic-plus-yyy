"""Indicator DNA — Dataclass & Configuration Loader

Implements: Override > CSV > JSON precedence
Internal: datetime; External: ISO string
"""

from dataclasses import dataclass, asdict, fields
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import csv
import os


@dataclass
class IndicatorDNA:
    """
    Indicator Identity Card.

    Fields:
    - id: Unique identifier
    - name: Display name
    - identity_type: Classification (e.g., "Risk Overlay", "Volatility Stress Indicator")
    - primary_use_case: Main application
    - secondary_use_case: Alternative application
    - one_line_summary: Marketing/narrative description
    - as_of: Last update (internally datetime; JSON stored as ISO string)
    """

    id: str
    name: str
    identity_type: str
    primary_use_case: str
    secondary_use_case: str
    one_line_summary: str
    as_of: datetime  # Internal: datetime; loaded from ISO string

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndicatorDNA":
        """
        Safely convert dict → IndicatorDNA.

        Handles as_of string → datetime conversion.
        Raises: ValueError if required fields missing or as_of invalid.
        """
        required_fields = {f.name for f in fields(cls)}
        missing = required_fields - set(data.keys())
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        # Convert as_of ISO string → datetime
        as_of_value = data.get("as_of")
        if isinstance(as_of_value, str):
            try:
                as_of = datetime.fromisoformat(as_of_value)
            except ValueError as e:
                raise ValueError(f"Invalid ISO date format for as_of: {as_of_value}") from e
        elif isinstance(as_of_value, datetime):
            as_of = as_of_value
        else:
            raise ValueError(f"as_of must be ISO string or datetime, got {type(as_of_value)}")

        return cls(
            id=data["id"],
            name=data["name"],
            identity_type=data["identity_type"],
            primary_use_case=data["primary_use_case"],
            secondary_use_case=data["secondary_use_case"],
            one_line_summary=data["one_line_summary"],
            as_of=as_of,
        )

    def to_dict(self, use_iso_for_as_of: bool = True) -> Dict[str, Any]:
        """
        Convert IndicatorDNA → dict.

        If use_iso_for_as_of=True, convert datetime → ISO string (for JSON export).
        """
        d = asdict(self)
        if use_iso_for_as_of and isinstance(d.get("as_of"), datetime):
            d["as_of"] = d["as_of"].isoformat()
        return d


class IndicatorDNALoader:
    """
    Load indicator DNA with precedence: override > CSV > JSON.

    Usage:
        loader = IndicatorDNALoader(json_path="config/indicator_dna.json")
        mapping = loader.load(csv_path="optional.csv", override_dict={...})
        dna = loader.get("hy_ig_spread")
    """

    def __init__(self, json_path: str) -> None:
        """
        Args:
            json_path: Path to config/indicator_dna.json
        """
        self.json_path = json_path
        self._cache: Dict[str, IndicatorDNA] = {}

    def load(
        self,
        csv_path: Optional[str] = None,
        override_dict: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, IndicatorDNA]:
        """
        Load indicator DNA with precedence: override > CSV > JSON.

        Returns: {indicator_id: IndicatorDNA, ...}

        Precedence:
        1. override_dict (highest priority)
        2. csv_path (if provided)
        3. json_path (default fallback)
        """
        # Start with JSON (base)
        dna_dict: Dict[str, Dict[str, Any]] = self._load_json()

        # Override with CSV (if provided)
        if csv_path:
            csv_data = self._load_csv(csv_path)
            dna_dict.update(csv_data)

        # Override with explicit override_dict (highest priority)
        if override_dict:
            dna_dict.update(override_dict)

        # Convert all to IndicatorDNA objects
        result: Dict[str, IndicatorDNA] = {}
        for ind_id, data in dna_dict.items():
            try:
                result[ind_id] = IndicatorDNA.from_dict(data)
            except ValueError as e:
                raise ValueError(f"Failed to load indicator {ind_id}: {e}") from e

        self._cache = result
        return result

    def _load_json(self) -> Dict[str, Dict[str, Any]]:
        """Load from JSON config file."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Config file not found: {self.json_path}")

        with open(self.json_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Expect: {"indicators": [{...}, {...}]}
        indicators_list = config.get("indicators", [])
        return {ind["id"]: ind for ind in indicators_list}

    def _load_csv(self, csv_path: str) -> Dict[str, Dict[str, Any]]:
        """Load from CSV file (override precedence)."""
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        result: Dict[str, Dict[str, Any]] = {}
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ind_id = row.get("id")
                if not ind_id:
                    continue
                # Keep row as raw mapping; IndicatorDNA.from_dict will validate/convert.
                result[ind_id] = dict(row)
        return result

    def get(self, indicator_id: str) -> Optional[IndicatorDNA]:
        """Retrieve cached indicator DNA by ID."""
        return self._cache.get(indicator_id)

    def get_all(self) -> Dict[str, IndicatorDNA]:
        """Return all loaded indicator DNA."""
        return self._cache.copy()

