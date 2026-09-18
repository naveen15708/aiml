"""Deterministic, lightweight models and explainers for the three dashboard domains."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import shap
from lime.lime_tabular import LimeTabularExplainer
from sklearn.ensemble import RandomForestClassifier


@dataclass(frozen=True)
class FeatureSpec:
    key: str
    label: str
    minimum: float
    maximum: float
    default: float
    step: float
    format: str
    description: str


@dataclass(frozen=True)
class DomainSpec:
    key: str
    title: str
    subtitle: str
    positive_label: str
    features: tuple[FeatureSpec, ...]
    seed: int


DOMAIN_SPECS: dict[str, DomainSpec] = {
    "Business lending": DomainSpec(
        "business",
        "Business Lending Decision System",
        "Pre-screen default risk before underwriting review.",
        "Default risk",
        (
            FeatureSpec("credit_score", "Credit score", 300, 850, 735, 1, "%.0f", "Higher is healthier"),
            FeatureSpec("debt_to_income", "Debt-to-income (%)", 0, 100, 32, 1, "%.0f", "Lower is healthier"),
            FeatureSpec("annual_income", "Annual income ($)", 20_000, 500_000, 145_000, 5_000, "%.0f", "Higher supports repayment"),
            FeatureSpec("cash_reserves", "Cash reserves ($)", 0, 250_000, 65_000, 5_000, "%.0f", "Liquidity buffer"),
            FeatureSpec("business_years", "Years in business", 0, 40, 8, 1, "%.0f", "Operating track record"),
            FeatureSpec("requested_amount", "Requested amount ($)", 5_000, 500_000, 75_000, 5_000, "%.0f", "Smaller relative requests are safer"),
        ),
        11,
    ),
    "Clinical care": DomainSpec(
        "clinical",
        "Clinical Risk Support System",
        "Screen for near-term deterioration risk; clinicians remain responsible for care.",
        "Clinical event risk",
        (
            FeatureSpec("heart_rate", "Heart rate (bpm)", 40, 180, 94, 1, "%.0f", "Persistent tachycardia can elevate risk"),
            FeatureSpec("systolic_bp", "Systolic BP (mmHg)", 70, 220, 118, 1, "%.0f", "Extremes can elevate risk"),
            FeatureSpec("temperature", "Temperature (°C)", 34, 42, 37.2, 0.1, "%.1f", "Fever or hypothermia can elevate risk"),
            FeatureSpec("respiratory_rate", "Respiratory rate (/min)", 8, 50, 18, 1, "%.0f", "Higher rates can signal distress"),
            FeatureSpec("oxygen_saturation", "Oxygen saturation (%)", 70, 100, 97, 1, "%.0f", "Lower saturation is concerning"),
            FeatureSpec("age", "Age (years)", 18, 100, 52, 1, "%.0f", "Risk generally rises with age"),
        ),
        23,
    ),
    "Investment": DomainSpec(
        "investment",
        "Investment Risk System",
        "Stress-test portfolio exposure and identify drawdown drivers.",
        "Portfolio drawdown risk",
        (
            FeatureSpec("volatility", "Annualized volatility (%)", 0, 80, 22, 1, "%.0f", "Lower is safer"),
            FeatureSpec("max_drawdown", "Historical max drawdown (%)", 0, 80, 18, 1, "%.0f", "Lower is safer"),
            FeatureSpec("equity_exposure", "Equity exposure (%)", 0, 100, 65, 1, "%.0f", "Diversification reduces concentration"),
            FeatureSpec("sector_concentration", "Top-sector concentration (%)", 0, 100, 28, 1, "%.0f", "Lower is safer"),
            FeatureSpec("sharpe_ratio", "Sharpe ratio", -2, 4, 1.1, 0.1, "%.1f", "Higher risk-adjusted return is healthier"),
            FeatureSpec("liquidity_days", "Days to liquidate", 0, 30, 3, 1, "%.0f", "Fewer days is safer"),
        ),
        37,
    ),
}


class DomainModel:
    """A small random-forest surrogate with TreeSHAP and LIME explanations."""

    def __init__(self, spec: DomainSpec) -> None:
        self.spec = spec
        self.feature_names = [feature.key for feature in spec.features]
        self.model = self._fit()
        self.background = self._training_frame(240)
        self.shap_explainer = shap.TreeExplainer(self.model, self.background)
        self.lime_explainer = LimeTabularExplainer(
            self.background.to_numpy(),
            feature_names=self.feature_names,
            class_names=["Low risk", "High risk"],
            mode="classification",
            discretize_continuous=False,
            random_state=spec.seed,
        )

    def _training_frame(self, rows: int) -> pd.DataFrame:
        rng = np.random.default_rng(self.spec.seed)
        data = {
            feature.key: rng.uniform(feature.minimum, feature.maximum, rows)
            for feature in self.spec.features
        }
        return pd.DataFrame(data, columns=self.feature_names)

    def _risk_function(self, frame: pd.DataFrame) -> np.ndarray:
        normalized = []
        for feature in self.spec.features:
            values = (frame[feature.key].to_numpy() - feature.minimum) / (feature.maximum - feature.minimum)
            if feature.key in {"debt_to_income", "requested_amount", "heart_rate", "systolic_bp",
                               "temperature", "respiratory_rate", "age", "volatility", "max_drawdown",
                               "equity_exposure", "sector_concentration", "liquidity_days"}:
                if feature.key in {"heart_rate", "systolic_bp", "temperature"}:
                    values = np.abs(values - 0.5) * 2
                normalized.append(values)
            else:
                normalized.append(1 - values)
        score = np.average(np.vstack(normalized), axis=0, weights=np.arange(1, len(normalized) + 1))
        return 1 / (1 + np.exp(-7 * (score - 0.5)))

    def _fit(self) -> RandomForestClassifier:
        frame = self._training_frame(900)
        probability = self._risk_function(frame)
        labels = (probability + np.random.default_rng(self.spec.seed + 1).normal(0, 0.08, len(frame)) > 0.52).astype(int)
        model = RandomForestClassifier(n_estimators=120, max_depth=7, random_state=self.spec.seed, min_samples_leaf=5)
        model.fit(frame, labels)
        return model

    def _frame(self, values: dict[str, float]) -> pd.DataFrame:
        missing = [name for name in self.feature_names if name not in values]
        if missing:
            raise ValueError(f"Missing features: {', '.join(missing)}")
        return pd.DataFrame([[float(values[name]) for name in self.feature_names]], columns=self.feature_names)

    def predict(self, values: dict[str, float]) -> dict[str, Any]:
        frame = self._frame(values)
        probability = float(self.model.predict_proba(frame)[0, 1])
        shap_values = self.shap_explainer.shap_values(frame)
        if isinstance(shap_values, list):
            attribution = np.asarray(shap_values[1][0], dtype=float)
            base_value = float(np.asarray(self.shap_explainer.expected_value)[1])
        else:
            raw = np.asarray(shap_values)
            attribution = raw[0, :, 1] if raw.ndim == 3 else raw[0]
            expected = np.asarray(self.shap_explainer.expected_value)
            base_value = float(expected[1] if expected.ndim else expected)
        factors = []
        for feature, contribution, value in zip(self.spec.features, attribution, frame.iloc[0]):
            factors.append({
                "key": feature.key,
                "label": feature.label,
                "value": float(value),
                "impact": float(contribution),
                "direction": "increases" if contribution >= 0 else "reduces",
            })
        factors.sort(key=lambda item: abs(item["impact"]), reverse=True)
        level = "High" if probability >= 0.66 else "Medium" if probability >= 0.38 else "Low"
        confidence = min(0.96, 0.55 + abs(probability - 0.5) * 0.8)
        return {
            "probability": probability,
            "level": level,
            "confidence": confidence,
            "factors": factors,
            "base_value": base_value,
            "plain_language": self._summary(level, probability, factors),
        }

    def lime(self, values: dict[str, float]) -> list[dict[str, Any]]:
        frame = self._frame(values)

        def predict_proba(array: np.ndarray) -> np.ndarray:
            return self.model.predict_proba(pd.DataFrame(array, columns=self.feature_names))

        explanation = self.lime_explainer.explain_instance(
            frame.iloc[0].to_numpy(), predict_proba, num_features=3
        )
        return [{"feature": label, "impact": float(weight)} for label, weight in explanation.as_list()]

    @staticmethod
    def _summary(level: str, probability: float, factors: list[dict[str, Any]]) -> str:
        lead = factors[:3]
        details = "; ".join(
            f"{item['label']} {item['direction']} risk (value: {item['value']:.2f})" for item in lead
        )
        return f"The model estimates {probability:.0%} {level.lower()} risk. " + details + ". Review this signal alongside domain context."


MODELS = {name: DomainModel(spec) for name, spec in DOMAIN_SPECS.items()}


def predict(domain: str, values: dict[str, float]) -> dict[str, Any]:
    """Predict and explain a scenario for a named dashboard domain."""
    if domain not in MODELS:
        raise ValueError(f"Unknown domain: {domain}")
    return MODELS[domain].predict(values)

