"""Transparent decision-support model for a small-business loan pre-screen."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Any


FEATURES = (
    ("credit_score", "Credit score", 0.30),
    ("debt_to_income", "Debt-to-income ratio", 0.20),
    ("annual_income", "Annual income", 0.20),
    ("cash_reserves", "Cash reserves", 0.15),
    ("business_years", "Years in business", 0.10),
    ("loan_to_income", "Requested loan vs income", 0.05),
)


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _number(payload: dict[str, Any], key: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{key} is required")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be a number") from exc
    if result < 0:
        raise ValueError(f"{key} cannot be negative")
    return result


def _quality(value: float, low: float, high: float) -> float:
    return _clamp((value - low) / (high - low))


def _risk_quality(value: float, good: float, bad: float) -> float:
    return _clamp((bad - value) / (bad - good))


@dataclass(frozen=True)
class Explanation:
    key: str
    label: str
    contribution: float
    quality: float
    direction: str
    detail: str


def assess(application: dict[str, Any]) -> dict[str, Any]:
    """Score an application and return an explanation for every model feature."""
    credit_score = _number(application, "credit_score")
    debt_to_income = _number(application, "debt_to_income")
    annual_income = _number(application, "annual_income")
    cash_reserves = _number(application, "cash_reserves")
    business_years = _number(application, "business_years")
    requested_amount = _number(application, "requested_amount")

    if not 300 <= credit_score <= 850:
        raise ValueError("credit_score must be between 300 and 850")
    if debt_to_income > 100:
        raise ValueError("debt_to_income must be between 0 and 100")
    if annual_income == 0:
        raise ValueError("annual_income must be greater than zero")

    loan_to_income = requested_amount / annual_income
    values = {
        "credit_score": _quality(credit_score, 300, 850),
        "debt_to_income": _risk_quality(debt_to_income, 20, 60),
        "annual_income": _quality(annual_income, 20_000, 250_000),
        "cash_reserves": _quality(cash_reserves, 0, 100_000),
        "business_years": _quality(business_years, 0, 10),
        "loan_to_income": _risk_quality(loan_to_income, 0.15, 1.0),
    }
    details = {
        "credit_score": f"{credit_score:.0f} credit score",
        "debt_to_income": f"{debt_to_income:.1f}% debt-to-income",
        "annual_income": f"${annual_income:,.0f} annual income",
        "cash_reserves": f"${cash_reserves:,.0f} cash reserves",
        "business_years": f"{business_years:.1f} years in business",
        "loan_to_income": f"{loan_to_income:.2f}x requested loan to income",
    }

    explanations = []
    score = 0.0
    for key, label, weight in FEATURES:
        quality = values[key]
        contribution = (quality - 0.5) * weight
        score += contribution
        explanations.append(
            Explanation(
                key=key,
                label=label,
                contribution=contribution,
                quality=quality,
                direction="supports" if contribution >= 0 else "weakens",
                detail=details[key],
            )
        )

    probability = 1 / (1 + exp(-8 * score))
    if probability >= 0.65:
        recommendation = "Likely eligible"
    elif probability >= 0.40:
        recommendation = "Needs review"
    else:
        recommendation = "Higher risk"

    confidence = min(0.96, 0.55 + abs(probability - 0.5) * 0.8)
    ranked = sorted(explanations, key=lambda item: abs(item.contribution), reverse=True)
    return {
        "recommendation": recommendation,
        "confidence": round(confidence, 3),
        "score": round(probability, 3),
        "summary": (
            "The strongest positive and negative factors are shown below. "
            "This is a pre-screening aid, not a lending decision."
        ),
        "factors": [
            {
                "key": item.key,
                "label": item.label,
                "impact": round(item.contribution, 4),
                "quality": round(item.quality, 3),
                "direction": item.direction,
                "detail": item.detail,
            }
            for item in ranked
        ],
        "methodology": {
            "type": "weighted scorecard",
            "weights": {key: weight for key, _, weight in FEATURES},
            "confidence_note": "Confidence reflects score separation from the review boundary and is not a probability of repayment.",
        },
    }
