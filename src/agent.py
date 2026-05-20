from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .document_loader import load_document_text
from .extractor import extract_fields, find_missing_fields
from .models import ClaimAssessment
from .router import assess_claim


def process_fnol(path: Path) -> ClaimAssessment:
    text = load_document_text(path)
    extracted = extract_fields(text)
    missing = find_missing_fields(extracted)
    return assess_claim(extracted, missing)


def process_fnol_to_json(path: Path, indent: int = 2) -> str:
    assessment = process_fnol(path)
    return json.dumps(assessment.to_json_dict(), indent=indent)


def process_fnol_dict(path: Path) -> dict[str, Any]:
    return process_fnol(path).to_json_dict()
