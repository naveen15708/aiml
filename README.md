# Explainable AI Multi-Domain Decision Support

This repository contains a runnable Streamlit hackathon prototype for an explainable decision-support system spanning business lending, clinical risk support, and investment risk.

## Included

- `app.py`: Streamlit dashboard entry point with domain switching
- `models.py`: deterministic synthetic model training, TreeSHAP attributions, and LIME explanations
- `components/`: reusable input, prediction, and explainability UI sections
- `model.py`, `server.py`, and `decision_support/`: retained legacy HTTP/scorecard API

## Run locally

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

The app uses deterministic synthetic data so it runs out of the box without downloading a dataset or model artifact. It is a prototype and must not be used as the sole basis for lending, clinical, or investment decisions.
