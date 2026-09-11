# app/

## What Streamlit is

[Streamlit](https://streamlit.io/) turns a plain Python script into an interactive web
app — no HTML/JS/frontend framework needed. You write normal Python, call functions
like `st.number_input(...)` or `st.button(...)` to render widgets, and Streamlit
reruns your script top-to-bottom whenever the user interacts with something. That's
the whole model: it's why `streamlit_app.py` reads like a script, not a web server.

This project uses it for one reason: a working demo you can click through is a much
faster way to convince someone the model works than asking them to read code or run
CLI commands.

## How to run it

```bash
source .venv/bin/activate   # if you haven't already (created by `make setup`)
python -m wine_origin train # only needed once, if models/model.joblib doesn't exist yet
streamlit run app/streamlit_app.py
```

Opens at `http://localhost:8501`. Stop it with `Ctrl+C`.

## What's in `streamlit_app.py`

- 13 number inputs, one per chemical measurement, defaulting to the dataset's rough
  averages
- a "fill with a random test-set sample" button, so you can try the model on real
  held-out data with one click instead of typing 13 numbers by hand
- the prediction plus a bar chart of class probabilities
- `@st.cache_resource` on model loading, so the (small) model is loaded once per
  session instead of on every interaction — this matters more as models get bigger
- a friendly `st.error(...)` message (not a stack trace) if no trained model is found,
  telling you to run `python -m wine_origin train` first
