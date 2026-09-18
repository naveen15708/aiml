from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def render_explanation(result: dict, lime_values: list[dict]) -> None:
    st.subheader("Why this result?")
    st.info(result["plain_language"])
    factors = pd.DataFrame(result["factors"])
    chart = factors.sort_values("impact")
    fig, ax = plt.subplots(figsize=(8, 3.5))
    colors = ["#ef4444" if value >= 0 else "#22c55e" for value in chart["impact"]]
    ax.barh(chart["label"], chart["impact"], color=colors)
    ax.axvline(0, color="#475569", linewidth=0.8)
    ax.set_xlabel("SHAP contribution to high-risk prediction")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)
    st.caption("SHAP: red bars push toward higher risk; green bars reduce risk for this specific scenario.")
    with st.expander("Compare with LIME local explanation"):
        st.dataframe(pd.DataFrame(lime_values), hide_index=True, use_container_width=True)
