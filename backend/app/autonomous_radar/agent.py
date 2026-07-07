from __future__ import annotations

from dataclasses import dataclass

from backend.app.autonomous_radar.ranking import RankedOpportunity


@dataclass(frozen=True)
class AgentDecision:
    decision: str
    reason: str
    risk: str
    action: str
    expected_outcome: str

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "reason": self.reason,
            "risk": self.risk,
            "action": self.action,
            "expected_outcome": self.expected_outcome,
        }


def decide_candidate(candidate: RankedOpportunity) -> AgentDecision:
    stage = candidate.opportunity.stage
    score = candidate.radar_score
    if score >= 90:
        decision = "TEST NOW"
        action = "Launch 3 creatives within 72 hours and reserve initial supplier samples."
        expected = "High chance of fast validation if hooks hold above 35%."
    elif score >= 80:
        decision = "TEST"
        action = "Run 3-5 videos over 7 days and validate supplier price before inventory."
        expected = "Good validation candidate with controlled budget."
    elif score >= 70:
        decision = "WATCH"
        action = "Monitor creator growth and competition for 7 days."
        expected = "May become testable if growth persists."
    else:
        decision = "SKIP"
        action = "Do not allocate test budget today."
        expected = "Insufficient near-term opportunity."
    risk = "HIGH" if stage in {"PEAK", "DECLINING"} else "MEDIUM" if score < 80 else "LOW"
    reason = f"{candidate.product.title}: {candidate.opportunity.reason} Lifecycle stage is {stage}."
    return AgentDecision(decision, reason, risk, action, expected)
