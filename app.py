"""Streamlit entry point for the Explainable AI multi-domain dashboard."""

from __future__ import annotations

import streamlit as st

from components.explainability import render_explanation
from components.prediction import render_prediction
from components.reporting import build_report_pdf
from components.what_if import render_counterfactual, render_inputs
from models import DOMAIN_SPECS, MODELS

st.set_page_config(page_title="XAI Decision Support", page_icon="XAI", layout="wide")
st.title("Explainable AI Decision Support")
st.markdown(
    "One interactive workspace for **business lending**, **clinical risk support**, and **investment risk**. "
    "Change any input to see the prediction and local explanation update."
)

domain = st.sidebar.radio("Choose a decision domain", list(DOMAIN_SPECS), index=0)
spec = DOMAIN_SPECS[domain]
model = MODELS[domain]
st.sidebar.divider()
st.sidebar.caption("Prototype model card")
st.sidebar.write("Synthetic, deterministic training data")
st.sidebar.write("Random forest + TreeSHAP + LIME")
st.sidebar.warning("Human review is required for consequential decisions.")

st.header(spec.title)
st.caption(spec.subtitle)
input_column, result_column = st.columns([0.9, 1.35], gap="large")
with input_column:
    values = render_inputs(spec, spec.key)
with result_column:
    result = model.predict(values)
    lime_values = model.lime(values)
    render_prediction(result)
    render_explanation(result, lime_values)

pdf_report = build_report_pdf(domain, values, result, lime_values)
st.download_button(
    label="Download report as PDF",
    data=pdf_report,
    file_name=f"{domain.lower().replace(' ', '_')}_decision_report.pdf",
    mime="application/pdf",
)

st.divider()
render_counterfactual(spec, model, values)
st.divider()
st.subheader("Current scenario details")
st.dataframe(
    [
        {"Feature": feature.label, "Current value": values[feature.key], "Meaning": feature.description}
        for feature in spec.features
    ],
    hide_index=True,
    width="stretch",
)
