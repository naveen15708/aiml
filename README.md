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

## Deploy on Render

1. Push this repository to GitHub or GitLab.
2. In Render, choose **New > Blueprint** and select the repository. Render will read `render.yaml`.
3. Confirm the service is a **Web Service**, then deploy. No environment variables are required.

The blueprint installs `requirements.txt` and starts Streamlit on Render's assigned `$PORT`. After the build completes, open the `onrender.com` URL shown in the service dashboard.

The app uses deterministic synthetic data so it runs out of the box without downloading a dataset or model artifact. It is a prototype and must not be used as the sole basis for lending, clinical, or investment decisions.
