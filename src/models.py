from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MANDATORY_FIELDS: list[str] = [
    "policyNumber",
    "policyholderName",
    "effectiveDates",
    "incidentDate",
    "incidentTime",
    "incidentLocation",
    "incidentDescription",
    "claimant",
    "thirdParties",
    "contactDetails",
    "assetType",
    "assetId",
    "estimatedDamage",
    "claimType",
    "attachments",
    "initialEstimate",
]

FIELD_LABELS: dict[str, str] = {
    "policyNumber": "Policy Number",
    "policyholderName": "Policyholder Name",
    "effectiveDates": "Effective Dates",
    "incidentDate": "Incident Date",
    "incidentTime": "Incident Time",
    "incidentLocation": "Incident Location",
    "incidentDescription": "Incident Description",
    "claimant": "Claimant",
    "thirdParties": "Third Parties",
    "contactDetails": "Contact Details",
    "assetType": "Asset Type",
    "assetId": "Asset ID",
    "estimatedDamage": "Estimated Damage",
    "claimType": "Claim Type",
    "attachments": "Attachments",
    "initialEstimate": "Initial Estimate",
}

FAST_TRACK_DAMAGE_THRESHOLD = 25_000

INVESTIGATION_KEYWORDS = ("fraud", "inconsistent", "staged")


@dataclass
class ClaimAssessment:
    extracted_fields: dict[str, Any]
    missing_fields: list[str]
    recommended_route: str
    reasoning: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "extractedFields": self.extracted_fields,
            "missingFields": self.missing_fields,
            "recommendedRoute": self.recommended_route,
            "reasoning": self.reasoning,
        }
