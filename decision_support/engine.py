"""Decision support engine with explainable recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class FactorImpact:
    """Represents a single predictor influencing a recommendation."""

    name: str
    weight: float
    direction: str
    explanation: str


@dataclass
class Recommendation:
    """Prediction result with explanation and confidence."""

    prediction: str
    confidence: float
    rationale: List[str]
    factors: List[FactorImpact] = field(default_factory=list)


class DecisionSupportSystem:
    """Simple explainable scoring model for decision support."""

    def __init__(self, model_name: str = "weighted-score-model") -> None:
        self.model_name = model_name

    def evaluate(self, scenario: Dict[str, Any]) -> Recommendation:
        """Evaluate a scenario and return a recommendation with explanations."""
        if not isinstance(scenario, dict) or not scenario:
            raise ValueError("scenario must be a non-empty dictionary")

        # The system converts factors into a score; features with higher weights push
        # the recommendation toward the preferred outcome.
        scoring = {
            "approve": 0.0,
            "reject": 0.0,
        }
        factors: List[FactorImpact] = []

        for name, value in scenario.items():
            normalized = self._normalize_factor(value)
            if name in {"risk_level", "uncertainty", "cost", "delay"}:
                weight = self._factor_weight(name, "reject")
                scoring["reject"] += normalized * weight
                scoring["approve"] -= normalized * weight
                factors.append(
                    FactorImpact(
                        name=name,
                        weight=weight,
                        direction="against",
                        explanation=f"{name} is elevated ({value}), which increases rejection risk.",
                    )
                )
            elif name in {"market_potential", "expected_value", "strategic_fit", "confidence"}:
                weight = self._factor_weight(name, "approve")
                scoring["approve"] += normalized * weight
                scoring["reject"] -= normalized * weight
                factors.append(
                    FactorImpact(
                        name=name,
                        weight=weight,
                        direction="for",
                        explanation=f"{name} is strong ({value}), which supports approval.",
                    )
                )
            else:
                # Unrecognized factors still contribute a mild, neutral effect.
                neutral_weight = 0.5
                scoring["approve"] += normalized * neutral_weight * 0.5
                scoring["reject"] += normalized * neutral_weight * 0.5
                factors.append(
                    FactorImpact(
                        name=name,
                        weight=neutral_weight,
                        direction="neutral",
                        explanation=f"{name} is considered, but it has a moderate and balanced influence.",
                    )
                )

        total = scoring["approve"] + scoring["reject"] if scoring["approve"] + scoring["reject"] != 0 else 1
        approve_share = (scoring["approve"] / total) * 100
        reject_share = (scoring["reject"] / total) * 100

        if approve_share >= reject_share:
            prediction = "approve"
            confidence = min(0.99, max(0.55, approve_share / 100))
        else:
            prediction = "reject"
            confidence = min(0.99, max(0.55, reject_share / 100))

        top_factors = sorted(factors, key=lambda item: abs(item.weight), reverse=True)[:3]
        rationale = [
            f"The model indicates a {prediction} decision with {confidence:.2%} confidence.",
            "The recommendation is based on the weighted impact of the scenario factors.",
        ]
        for factor in top_factors:
            rationale.append(
                f"{factor.name} contributes {factor.direction} to the decision: {factor.explanation}"
            )

        return Recommendation(
            prediction=prediction,
            confidence=confidence,
            rationale=rationale,
            factors=top_factors,
        )

    def _normalize_factor(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return max(0.0, min(float(value), 1.0))
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"low", "weak", "minor", "unlikely"}:
                return 0.2
            if lowered in {"moderate", "medium", "mixed", "possible"}:
                return 0.5
            if lowered in {"high", "strong", "major", "likely"}:
                return 0.8
            if lowered in {"critical", "very_high", "very_highly"}:
                return 1.0
            return 0.5
        return 0.5

    def _factor_weight(self, factor_name: str, outcome: str) -> float:
        weights = {
            "risk_level": 1.8,
            "uncertainty": 1.5,
            "cost": 1.3,
            "delay": 1.2,
            "market_potential": 1.8,
            "expected_value": 1.9,
            "strategic_fit": 1.6,
            "confidence": 1.4,
        }
        return weights.get(factor_name, 1.0)

    def explain(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Return an explainable summary for a given scenario."""
        recommendation = self.evaluate(scenario)
        return {
            "model": self.model_name,
            "prediction": recommendation.prediction,
            "confidence": round(recommendation.confidence, 4),
            "major_factors": [
                {
                    "name": factor.name,
                    "weight": round(factor.weight, 2),
                    "direction": factor.direction,
                    "explanation": factor.explanation,
                }
                for factor in recommendation.factors
            ],
            "rationale": recommendation.rationale,
        }

    def recommend(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience wrapper for a user-facing recommendation."""
        return self.explain(scenario)
