# Streamlit Starter App

A beginner-friendly Streamlit project that demonstrates:

- multipage navigation
- a home page
- CSV upload
- interactive charts
- session state
- custom logic
- downloadable results

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
streamlit_starter_app/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── pages/
    ├── home.py
    ├── upload_and_explore.py
    ├── custom_logic.py
    └── about.py
```

## Notes

- Upload a CSV on the Upload + Charts page.
- The Custom Logic page will use your uploaded data if available.
- This is a clean starter template you can extend into a business app, analytics tool, or AI workflow.