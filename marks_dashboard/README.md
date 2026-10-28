<!-- Layer: Documentation Layer -->
# 🎓 Student Marks Dashboard

A modern, lightweight, and beginner-friendly Student Marks Dashboard built using **Streamlit** (Frontend + Backend) and **Pandas** for file-based CSV persistence.

Designed for single-user local usage on any laptop with no complex database servers or authentication required.

---

## 🏛️ Architectural Overview & Layer Separation

Although this application is packaged in a simple single-folder structure, it adheres strictly to a clean 3-tier architectural separation:

```
marks_dashboard/
├── app.py              # Layer 1: Presentation / Frontend Layer (Streamlit UI)
├── data_store.py        # Layer 2 & 3: Persistence & Backend Validation Layer
├── students.csv         # Database Store (created automatically on first run)
├── requirements.txt     # Pinned Python package dependencies
└── README.md            # Documentation & setup guide
```

### Why the Persistence Layer is Separated (`data_store.py`)
All reading and writing of `students.csv`, input validation, and business calculations (such as totals, averages, grades, topper identification) reside entirely inside `data_store.py`. 

> **Swapping to SQLite / PostgreSQL:**
> Because `app.py` only interacts with `data_store.py` via standardized methods (`init_data_store`, `get_all_students`, `add_student`, `delete_student`) and receives standardized response dictionaries with HTTP status codes (200, 201, 400, 404, 409), the underlying CSV storage could be swapped out for an SQLite or PostgreSQL database in `data_store.py` without having to change a single line in `app.py`!

---

## ✨ Features

1. **Sidebar Student Enrollment Form:**
   - Add new students with Full Name, unique Roll Number, and Subject Marks (Maths, Science, English: 0-100).
   - Validates data on the backend and surfaces clear feedback with HTTP-style response codes.
2. **Automated CSV Persistence & Auto-Seeding:**
   - Automatically initializes `students.csv` with headers and 5 realistic sample records on first run.
3. **Comprehensive Performance Table:**
   - Displays all students with computed **Total** (out of 300), **Average** (percentage), and **Grade**.
   - Grading scale:
     - **A**: Average $\ge 90$
     - **B**: Average $\ge 75$ (and $< 90$)
     - **C**: Average $\ge 60$ (and $< 75$)
     - **D**: Average $\ge 40$ (and $< 60$)
     - **F**: Average $< 40$
4. **Class Topper Highlight Box:**
   - High-visibility banner celebrating the highest-scoring student in the class, displaying their Name, Roll Number, Total Marks, Average %, and Grade.
5. **Subject-Wise Average Bar Chart:**
   - Interactive bar chart illustrating class averages across Mathematics, Science, and English.
6. **CSV Export / Download:**
   - One-click button to download the calculated table (with Totals, Averages, and Grades) as a timestamped CSV report.
7. **Stretch Goal 1: Delete Student:**
   - Interactive dropdown in the sidebar to delete an existing student record with safety confirmation.
8. **Stretch Goal 2: Subject-Wise Pass/Fail Pie Chart:**
   - Interactive donut chart showing Pass ($\ge 40$) vs Fail ($< 40$) distribution per selected subject.
9. **Interactive Search & Grade Distribution:**
   - Instant search filter by name or roll number and an expandable grade distribution chart.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python**: Version 3.9 or higher (tested on Python 3.12).
- **pip**: Python package manager.

### 2. Installation
Open your terminal / command prompt, navigate to the `marks_dashboard` directory, and install the pinned dependencies:

```bash
cd marks_dashboard
pip install -r requirements.txt
```

### 3. Running the Dashboard
Launch the Streamlit dashboard using:

```bash
streamlit run app.py
```

### 4. URL to Open
Once started, Streamlit will open your default browser automatically, or you can open:

- **Local URL**: [http://localhost:8501](http://localhost:8501)
- **Network URL**: Displayed in the terminal output if accessing from another device on the same local network.

---

## 🛡️ Backend Validation & Status Codes

The backend persistence layer (`data_store.py`) validates every request and returns structured responses:

| HTTP Status | Meaning | Scenario |
|:---:|:---|:---|
| **`200 OK`** | Success | Retrieved student records or successfully deleted student. |
| **`201 Created`** | Created | Successfully validated and added a new student to `students.csv`. |
| **`400 Bad Request`** | Validation Error | Missing name, non-numeric marks, or marks outside range `[0, 100]`. |
| **`404 Not Found`** | Not Found | Attempted to delete a student whose roll number does not exist. |
| **`409 Conflict`** | Duplicate | A student with the provided Roll Number already exists. |
| **`500 Internal Error`**| Server Error | Unexpected file I/O or system failure. |

---

## 📦 Pinned Dependencies (`requirements.txt`)

- `streamlit==1.66.1`: Modern web application framework.
- `pandas==3.1.0`: High-performance data manipulation and CSV persistence.
- `plotly==7.1.0`: Interactive charts and data visualizations.
