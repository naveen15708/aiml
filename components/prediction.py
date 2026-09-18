from __future__ import annotations

import streamlit as st


def render_prediction(result: dict) -> None:
    probability = result["probability"]
    color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}[result["level"]]
    st.subheader("Decision signal")
    left, right, confidence = st.columns(3)
    left.metric("Risk category", f"{color} {result['level']}")
    right.metric("Risk probability", f"{probability:.0%}")
    confidence.metric("Model confidence", f"{result['confidence']:.0%}")
    st.progress(probability, text=f"{probability:.0%} estimated risk")
    st.caption("Probability estimates the modeled risk event. Confidence reflects score separation from the review boundary, not certainty.")
    st.caption("Decision support only: human review remains required for lending, clinical, and investment use.")
