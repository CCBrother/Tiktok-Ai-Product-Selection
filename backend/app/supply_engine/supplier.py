from __future__ import annotations

from dataclasses import dataclass

from backend.app.utils.math import clamp


@dataclass(frozen=True)
class SupplierProfile:
    supplier_name: str
    platform: str
    factory_type: str
    location: str
    price: float
    moq: int
    lead_time: int
    monthly_capacity: int
    customization_ability: float = 60
    certification: float = 60
    export_experience: float = 60
    factory_capability: float = 60


def score_supplier(profile: SupplierProfile) -> float:
    moq_score = clamp(100 - max(profile.moq - 50, 0) / 5)
    speed_score = clamp(100 - max(profile.lead_time - 5, 0) * 4)
    capacity_score = clamp(profile.monthly_capacity / 100)
    compliance_score = (profile.certification + profile.export_experience) / 2
    return round(
        clamp(
            profile.factory_capability * 0.25
            + moq_score * 0.2
            + speed_score * 0.2
            + profile.customization_ability * 0.15
            + capacity_score * 0.1
            + compliance_score * 0.1
        ),
        2,
    )


def recommended_supplier_profile(category: str | None) -> dict:
    normalized = (category or "").lower()
    if "kitchen" in normalized:
        return {"factory_type": "Zhejiang small appliance factory", "moq": 300, "lead_time": 15, "certification": ["FDA", "UL/ETL if electric"]}
    if "beauty" in normalized:
        return {"factory_type": "Guangdong beauty device factory", "moq": 200, "lead_time": 12, "certification": ["FDA cosmetics review", "MSDS if battery"]}
    if "pet" in normalized:
        return {"factory_type": "Jiangsu pet supplies manufacturer", "moq": 500, "lead_time": 18, "certification": ["material safety", "California Prop 65 check"]}
    return {"factory_type": "Yiwu general goods factory", "moq": 200, "lead_time": 10, "certification": ["export invoice", "basic material compliance"]}
