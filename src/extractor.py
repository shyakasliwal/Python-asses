from __future__ import annotations

import re
from typing import Any

# Maps canonical field keys to one or more label patterns in FNOL documents.
FIELD_PATTERNS: dict[str, list[str]] = {
    "policyNumber": [r"Policy\s+Number\s*:\s*(.+)"],
    "policyholderName": [r"Policyholder\s+Name\s*:\s*(.+)"],
    "effectiveDates": [r"Effective\s+Dates?\s*:\s*(.+)"],
    "incidentDate": [r"Incident\s+Date\s*:\s*(.+)", r"Date\s+of\s+Loss\s*:\s*(.+)"],
    "incidentTime": [r"Incident\s+Time\s*:\s*(.+)", r"Time\s+of\s+Loss\s*:\s*(.+)"],
    "incidentLocation": [r"Incident\s+Location\s*:\s*(.+)", r"Location\s*:\s*(.+)"],
    "incidentDescription": [
        r"Incident\s+Description\s*:\s*(.+)",
        r"Description\s+of\s+Loss\s*:\s*(.+)",
        r"Description\s*:\s*(.+)",
    ],
    "claimant": [r"Claimant\s*:\s*(.+)"],
    "thirdParties": [r"Third\s+Parties?\s*:\s*(.+)"],
    "contactDetails": [r"Contact\s+Details?\s*:\s*(.+)"],
    "assetType": [r"Asset\s+Type\s*:\s*(.+)"],
    "assetId": [r"Asset\s+ID\s*:\s*(.+)", r"Asset\s+Identifier\s*:\s*(.+)"],
    "estimatedDamage": [
        r"Estimated\s+Damage\s*:\s*(.+)",
        r"Damage\s+Estimate\s*:\s*(.+)",
    ],
    "claimType": [r"Claim\s+Type\s*:\s*(.+)"],
    "attachments": [r"Attachments?\s*:\s*(.+)"],
    "initialEstimate": [r"Initial\s+Estimate\s*:\s*(.+)"],
}

PLACEHOLDER_VALUES = {
    "",
    "n/a",
    "na",
    "none",
    "not provided",
    "unknown",
    "tbd",
    "—",
    "-",
}


def _first_match(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            if value.lower() not in PLACEHOLDER_VALUES:
                return value
    return None


def _parse_money(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = re.sub(r"[^\d.]", "", value.replace(",", ""))
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_fields(text: str) -> dict[str, Any]:
    extracted: dict[str, Any] = {}
    for key, patterns in FIELD_PATTERNS.items():
        raw = _first_match(text, patterns)
        if raw is not None:
            extracted[key] = raw

    damage_raw = extracted.get("estimatedDamage")
    damage_amount = _parse_money(damage_raw if isinstance(damage_raw, str) else None)
    if damage_amount is not None:
        extracted["estimatedDamageAmount"] = damage_amount

    initial_raw = extracted.get("initialEstimate")
    initial_amount = _parse_money(initial_raw if isinstance(initial_raw, str) else None)
    if initial_amount is not None:
        extracted["initialEstimateAmount"] = initial_amount

    return extracted


def find_missing_fields(extracted: dict[str, Any]) -> list[str]:
    from .models import MANDATORY_FIELDS

    missing: list[str] = []
    for key in MANDATORY_FIELDS:
        value = extracted.get(key)
        if value is None:
            missing.append(key)
            continue
        if isinstance(value, str) and value.strip().lower() in PLACEHOLDER_VALUES:
            missing.append(key)
    return missing


def find_inconsistencies(extracted: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    damage = extracted.get("estimatedDamageAmount")
    initial = extracted.get("initialEstimateAmount")
    if damage is not None and initial is not None:
        if abs(damage - initial) > max(damage, initial) * 0.5:
            issues.append(
                f"Estimated damage ({damage:,.0f}) differs significantly from "
                f"initial estimate ({initial:,.0f})."
            )
    return issues
