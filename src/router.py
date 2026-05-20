from __future__ import annotations

from typing import Any

from .models import (
    FAST_TRACK_DAMAGE_THRESHOLD,
    INVESTIGATION_KEYWORDS,
    ClaimAssessment,
    FIELD_LABELS,
)


def _damage_amount(extracted: dict[str, Any]) -> float | None:
    amount = extracted.get("estimatedDamageAmount")
    if isinstance(amount, (int, float)):
        return float(amount)
    return None


def _description_text(extracted: dict[str, Any]) -> str:
    desc = extracted.get("incidentDescription", "")
    return desc.lower() if isinstance(desc, str) else ""


def _claim_type(extracted: dict[str, Any]) -> str:
    claim = extracted.get("claimType", "")
    return claim.lower().strip() if isinstance(claim, str) else ""


def determine_route(
    extracted: dict[str, Any],
    missing_fields: list[str],
    inconsistencies: list[str],
) -> tuple[str, str]:
    reasons: list[str] = []

    description = _description_text(extracted)
    for keyword in INVESTIGATION_KEYWORDS:
        if keyword in description:
            reasons.append(
                f"Incident description contains '{keyword}', triggering investigation review."
            )
            return "Investigation Flag", " ".join(reasons)

    claim_type = _claim_type(extracted)
    if "injury" in claim_type or claim_type in {"bodily injury", "personal injury"}:
        reasons.append("Claim type is injury-related; routed to specialist handlers.")
        return "Specialist Queue", " ".join(reasons)

    if missing_fields:
        labels = [FIELD_LABELS.get(f, f) for f in missing_fields]
        reasons.append(
            f"Mandatory fields missing or incomplete: {', '.join(labels)}."
        )
        if inconsistencies:
            reasons.append(" ".join(inconsistencies))
        return "Manual Review", " ".join(reasons)

    if inconsistencies:
        reasons.append(" ".join(inconsistencies))
        return "Manual Review", " ".join(reasons)

    damage = _damage_amount(extracted)
    if damage is not None and damage < FAST_TRACK_DAMAGE_THRESHOLD:
        reasons.append(
            f"Estimated damage ({damage:,.0f}) is below "
            f"{FAST_TRACK_DAMAGE_THRESHOLD:,.0f}; eligible for fast-track processing."
        )
        return "Fast-track", " ".join(reasons)

    if damage is not None:
        reasons.append(
            f"Estimated damage ({damage:,.0f}) meets or exceeds the fast-track "
            f"threshold ({FAST_TRACK_DAMAGE_THRESHOLD:,.0f}); standard processing applies."
        )
    else:
        reasons.append(
            "Damage amount could not be parsed numerically; defaulting to standard workflow."
        )
    return "Standard Processing", " ".join(reasons)


def assess_claim(extracted: dict[str, Any], missing_fields: list[str]) -> ClaimAssessment:
    from .extractor import find_inconsistencies

    inconsistencies = find_inconsistencies(extracted)
    route, reasoning = determine_route(extracted, missing_fields, inconsistencies)
    return ClaimAssessment(
        extracted_fields=extracted,
        missing_fields=missing_fields,
        recommended_route=route,
        reasoning=reasoning,
    )
