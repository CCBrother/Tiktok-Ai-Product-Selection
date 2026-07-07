from __future__ import annotations


def opportunity_level(score: float) -> str:
    if score >= 90:
        return "S"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    return "D"


def recommended_action(level: str) -> str:
    return {
        "S": "Launch immediately",
        "A": "Strong test",
        "B": "Monitor",
        "C": "Low priority",
        "D": "Ignore",
    }[level]


def decision_from_level(level: str) -> str:
    return {
        "S": "LAUNCH",
        "A": "TEST",
        "B": "WATCH",
        "C": "WATCH",
        "D": "SKIP",
    }[level]
