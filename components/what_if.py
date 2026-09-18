from __future__ import annotations

import streamlit as st

from models import DomainModel, DomainSpec


def render_inputs(spec: DomainSpec, key_prefix: str) -> dict[str, float]:
    values: dict[str, float] = {}
    st.subheader("Scenario inputs")
    for feature in spec.features:
        values[feature.key] = st.slider(
            feature.label,
            min_value=float(feature.minimum),
            max_value=float(feature.maximum),
            value=float(feature.default),
            step=float(feature.step),
            help=feature.description,
            key=f"{key_prefix}_{feature.key}",
        )
    return values


def render_counterfactual(spec: DomainSpec, model: DomainModel, values: dict[str, float]) -> None:
    """Compare the current scenario with a user-controlled counterfactual."""
    st.subheader("What-if simulator")
    st.caption("Move up to two high-signal variables to see how the modeled risk changes.")
    selectable = list(spec.features)
    first, second = st.columns(2)
    with first:
        first_feature = st.selectbox(
            "Variable 1", selectable, format_func=lambda feature: feature.label, key=f"{spec.key}_what_if_first"
        )
        first_value = st.slider(
            f"Scenario value: {first_feature.label}",
            min_value=float(first_feature.minimum),
            max_value=float(first_feature.maximum),
            value=float(values[first_feature.key]),
            step=float(first_feature.step),
            key=f"{spec.key}_what_if_{first_feature.key}",
        )
    with second:
        remaining = [feature for feature in selectable if feature.key != first_feature.key]
        second_feature = st.selectbox(
            "Variable 2", remaining, format_func=lambda feature: feature.label, key=f"{spec.key}_what_if_second"
        )
        second_value = st.slider(
            f"Scenario value: {second_feature.label}",
            min_value=float(second_feature.minimum),
            max_value=float(second_feature.maximum),
            value=float(values[second_feature.key]),
            step=float(second_feature.step),
            key=f"{spec.key}_what_if_{second_feature.key}",
        )

    counterfactual = dict(values)
    counterfactual[first_feature.key] = first_value
    counterfactual[second_feature.key] = second_value
    baseline = model.predict(values)
    scenario = model.predict(counterfactual)
    delta = scenario["probability"] - baseline["probability"]
    left, right, change = st.columns(3)
    left.metric("Current risk", f"{baseline['probability']:.0%}", baseline["level"])
    right.metric("What-if risk", f"{scenario['probability']:.0%}", scenario["level"])
    change.metric("Risk change", f"{delta:+.0%}", delta_color="inverse")
