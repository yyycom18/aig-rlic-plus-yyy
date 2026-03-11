"""FastAPI app exposing Indicator DNA cards as JSON.

Optional endpoint used for Task 1 auditability:
- GET /api/indicator_dna → returns the contents of indicator_dna_cards.json
"""

from __future__ import annotations

from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


app = FastAPI(title="Indicator DNA API")

BASE_DIR = Path(__file__).resolve().parents[1]
CARDS_PATH = BASE_DIR / "data" / "indicator_dna_cards.json"


@app.get("/api/indicator_dna")
async def get_indicator_dna():
    """Return the raw indicator_dna_cards.json content."""
    try:
        with CARDS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="indicator_dna_cards.json not found")
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=str(exc))
    return JSONResponse(content=data)

