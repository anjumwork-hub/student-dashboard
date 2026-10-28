# Student Marks Dashboard

A complete Streamlit-based Student Marks Dashboard with CSV persistence and academic analytics.

The project is located in the [`marks_dashboard`](./marks_dashboard) folder:
```
marks_dashboard/
├── app.py              # Presentation / Frontend Layer (Streamlit UI)
├── data_store.py        # Persistence & Backend Validation Layer
├── students.csv         # CSV Database (created on first run)
├── requirements.txt     # Pinned Python dependencies
└── README.md            # Detailed documentation
```

## Quick Start

```bash
cd marks_dashboard
pip install -r requirements.txt
streamlit run app.py
```

Open your browser at `http://localhost:8501`.
