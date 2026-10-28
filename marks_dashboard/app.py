# ==============================================================================
# Layer: Presentation / Frontend Layer (Streamlit UI & User Interaction)
# ------------------------------------------------------------------------------
# ARCHITECTURAL NOTE:
# This file serves as the "presentation layer" of the Student Marks Dashboard.
# It communicates exclusively with data_store.py (the persistence & backend logic layer)
# to fetch data, invoke backend business operations, and receive standardized
# HTTP status responses (200, 201, 400, 404, 409).
# No direct low-level file I/O is performed in this file.
# ==============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import backend persistence functions and business analytics from data_store.py
import data_store as ds

# ------------------------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Marks Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# Custom CSS for Modern, Premium Visual Aesthetics
# ------------------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Font: Inter / Outfit styling */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    /* Gradient Hero Header */
    .hero-banner {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
        padding: 24px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);
    }
    .hero-title {
        font-size: 1.9rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 0.98rem;
        opacity: 0.9;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Highlighted Class Topper Card */
    .topper-card {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(245, 158, 11, 0.15);
        color: #78350f;
        position: relative;
        overflow: hidden;
    }
    .topper-badge {
        display: inline-block;
        background: #f59e0b;
        color: white;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .topper-name {
        font-size: 1.4rem;
        font-weight: 800;
        color: #92400e;
        margin: 0;
    }
    .topper-roll {
        font-size: 0.85rem;
        color: #b45309;
        margin-top: 2px;
        margin-bottom: 12px;
    }
    .topper-metric-grid {
        display: flex;
        gap: 16px;
        margin-top: 8px;
    }
    .topper-stat-box {
        background: rgba(255, 255, 255, 0.85);
        padding: 8px 12px;
        border-radius: 10px;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
    .topper-stat-label {
        font-size: 0.72rem;
        color: #92400e;
        text-transform: uppercase;
        font-weight: 600;
    }
    .topper-stat-value {
        font-size: 1.15rem;
        font-weight: 800;
        color: #78350f;
    }

    /* Standard Metric Card */
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
    }
    .stat-label {
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .stat-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #1e293b;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Section Headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 28px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Sidebar Styling */
    .sidebar-section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #334155;
        margin-top: 10px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Initialize the Backend Persistence Layer
# ------------------------------------------------------------------------------
# Ensures students.csv exists with headers and 3-5 sample records if first run
init_response = ds.init_data_store()


# ------------------------------------------------------------------------------
# Sidebar: 1. Add Student Form & Stretch Goal: Delete Student
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎓 Student Records Panel")
    st.markdown("Use this panel to enroll students or remove existing records.")
    st.divider()

    # Form to add a new student
    st.markdown("<div class='sidebar-section-title'>➕ Add New Student</div>", unsafe_allow_html=True)
    
    with st.form("add_student_form", clear_on_submit=True):
        student_name = st.text_input(
            "Student Full Name *",
            placeholder="e.g., Sarah Jenkins",
            help="Enter the student's legal or registered name"
        )
        
        roll_number = st.text_input(
            "Roll Number / ID *",
            placeholder="e.g., 106",
            help="Unique student identification number"
        )
        
        st.markdown("**Enter Subject Marks (0 - 100):**")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            maths_marks = st.number_input(
                "Maths",
                min_value=0,
                max_value=100,
                value=75,
                step=1,
                help="Mathematics score (0-100)"
            )
        with col_m2:
            science_marks = st.number_input(
                "Science",
                min_value=0,
                max_value=100,
                value=80,
                step=1,
                help="Science score (0-100)"
            )
            
        english_marks = st.number_input(
            "English",
            min_value=0,
            max_value=100,
            value=85,
            step=1,
            help="English score (0-100)"
        )

        submit_btn = st.form_submit_btn = st.form_submit_button("Save Student Record", use_container_width=True)

        if submit_btn:
            # Delegate to Backend Persistence Layer for input validation & CSV writing
            response = ds.add_student(
                name=student_name,
                roll_no=roll_number,
                maths=int(maths_marks),
                science=int(science_marks),
                english=int(english_marks)
            )

            # Check HTTP-style response status code from backend
            if response["status_code"] == 201:
                st.success(f"✅ [HTTP 201 Created] {response['message']}")
                st.rerun()
            elif response["status_code"] == 409:
                st.error(f"⚠️ [HTTP 409 Conflict] {response['message']}")
            else:
                st.error(f"❌ [HTTP {response['status_code']} Bad Request] {response['message']}")

    st.divider()

    # --------------------------------------------------------------------------
    # STRETCH GOAL: Delete Student Option
    # --------------------------------------------------------------------------
    st.markdown("<div class='sidebar-section-title'>🗑️ Delete Student (Stretch Goal)</div>", unsafe_allow_html=True)
    
    # Retrieve current students to populate dropdown
    current_data_resp = ds.get_all_students()
    current_df = current_data_resp["data"]

    if not current_df.empty:
        # Create a user-friendly label map: "Roll - Name"
        student_options = {
            f"{row['roll_no']} - {row['name']}": str(row['roll_no'])
            for _, row in current_df.iterrows()
        }
        
        selected_option = st.selectbox(
            "Select student to remove",
            options=list(student_options.keys()),
            help="Select student by Roll Number and Name to delete"
        )
        
        selected_roll = student_options[selected_option]

        # Use an expander for confirmation safety
        with st.expander("⚠️ Confirm Deletion", expanded=False):
            st.caption(f"Are you sure you want to delete **{selected_option}**? This cannot be undone.")
            if st.button("Permanently Delete", type="primary", use_container_width=True):
                del_res = ds.delete_student(selected_roll)
                if del_res["status_code"] == 200:
                    st.success(f"✅ [HTTP 200 OK] {del_res['message']}")
                    st.rerun()
                else:
                    st.error(f"❌ [HTTP {del_res['status_code']}] {del_res['message']}")
    else:
        st.info("No students available to delete.")


# ------------------------------------------------------------------------------
# Main Presentation Dashboard
# ------------------------------------------------------------------------------

# Hero Header Banner
st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">📊 Student Marks & Academic Performance Dashboard</h1>
    <p class="hero-subtitle">Single-user local dashboard with automated CSV persistence, grading metrics, and class analytics.</p>
</div>
""", unsafe_allow_html=True)

# Fetch latest dataset from backend
data_response = ds.get_all_students()

if data_response["status_code"] != 200:
    st.error(f"❌ [HTTP {data_response['status_code']}] {data_response['message']}")
    st.stop()

raw_df = data_response["data"]

# Compute business metrics (Total, Average, Grade, Topper, Subject Averages, Pass/Fail)
analytics = ds.compute_student_analytics(raw_df)
processed_df = analytics["processed_df"]
topper = analytics["topper"]
overall_stats = analytics["overall_stats"]
subject_averages = analytics["subject_averages"]
pass_fail_stats = analytics["pass_fail_stats"]

# ------------------------------------------------------------------------------
# Feature 5: Highlighted Class Topper Metric Box & Summary Cards
# ------------------------------------------------------------------------------
col_topper, col_stat1, col_stat2, col_stat3 = st.columns([1.5, 1, 1, 1])

with col_topper:
    if topper:
        st.markdown(f"""
        <div class="topper-card">
            <span class="topper-badge">🏆 Class Topper</span>
            <div class="topper-name">{topper['name']}</div>
            <div class="topper-roll">Roll No: <strong>{topper['roll_no']}</strong> | Grade: <strong>{topper['grade']}</strong></div>
            <div class="topper-metric-grid">
                <div class="topper-stat-box">
                    <div class="topper-stat-label">Total Marks</div>
                    <div class="topper-stat-value">{topper['total']}/300</div>
                </div>
                <div class="topper-stat-box">
                    <div class="topper-stat-label">Average</div>
                    <div class="topper-stat-value">{topper['average']}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No topper data available yet.")

with col_stat1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total Students</div>
        <div class="stat-value">{overall_stats['total_students']}</div>
        <div style="font-size: 0.78rem; color: #10b981; margin-top: 4px;">Enrolled in class</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Class Average</div>
        <div class="stat-value">{overall_stats['class_average']}%</div>
        <div style="font-size: 0.78rem; color: #6366f1; margin-top: 4px;">Across 3 subjects</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Pass Rate</div>
        <div class="stat-value">{overall_stats['overall_pass_rate']}%</div>
        <div style="font-size: 0.78rem; color: #f59e0b; margin-top: 4px;">Passed all subjects</div>
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# Feature 3: Show All Students Table with Total, Average, and Grade Columns
# ------------------------------------------------------------------------------
st.markdown("<div class='section-title'>📋 Student Academic Records</div>", unsafe_allow_html=True)

if not processed_df.empty:
    # Rename columns for clean, elegant display
    display_df = processed_df.copy()
    display_df.rename(columns={
        "roll_no": "Roll Number",
        "name": "Student Name",
        "maths": "Maths (100)",
        "science": "Science (100)",
        "english": "English (100)",
        "total": "Total (300)",
        "average": "Average (%)",
        "grade": "Grade"
    }, inplace=True)

    # Optional search bar to quickly filter students
    col_filter, col_spacer, col_dl = st.columns([2, 1, 1.2])
    with col_filter:
        search_query = st.text_input("🔍 Search by Name or Roll Number", placeholder="Filter table...", label_visibility="collapsed")
    
    if search_query:
        mask = (
            display_df["Student Name"].str.contains(search_query, case=False, na=False) |
            display_df["Roll Number"].astype(str).str.contains(search_query, case=False, na=False)
        )
        filtered_df = display_df[mask]
    else:
        filtered_df = display_df

    # Render interactive data table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Average (%)": st.column_config.ProgressColumn(
                "Average (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Grade": st.column_config.TextColumn(
                "Grade",
                help="A >= 90, B >= 75, C >= 60, D >= 40, F < 40"
            )
        }
    )

    # --------------------------------------------------------------------------
    # Feature 6: Download Button as CSV
    # --------------------------------------------------------------------------
    with col_dl:
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Table as CSV",
            data=csv_bytes,
            file_name=f"student_marks_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.caption("Grading Scale: **A** (≥90%) | **B** (≥75%) | **C** (≥60%) | **D** (≥40%) | **F** (<40%)")

else:
    st.warning("No student records found in the database. Add your first student using the sidebar form.")


# ------------------------------------------------------------------------------
# Feature 4 & Stretch Goal: Analytics & Visualizations
# ------------------------------------------------------------------------------
st.markdown("<div class='section-title'>📈 Class Performance & Subject Analytics</div>", unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns(2)

# Feature 4: Bar chart of average marks per subject
with col_chart1:
    st.markdown("##### 📊 Average Marks per Subject")
    subj_df = pd.DataFrame({
        "Subject": list(subject_averages.keys()),
        "Average Marks": list(subject_averages.values())
    })

    fig_bar = px.bar(
        subj_df,
        x="Subject",
        y="Average Marks",
        text="Average Marks",
        color="Subject",
        color_discrete_sequence=["#4f46e5", "#06b6d4", "#10b981"],
        range_y=[0, 100]
    )
    fig_bar.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        marker=dict(line=dict(width=1, color='#1e293b'))
    )
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis_title="Average Marks (out of 100)",
        xaxis_title="",
        showlegend=False,
        height=320
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Stretch Goal: Subject-wise Pass / Fail Pie Chart
with col_chart2:
    st.markdown("##### 🥧 Subject-wise Pass/Fail Ratio (Stretch Goal)")
    
    # Subject selector for pass/fail breakdown
    selected_pie_subj = st.selectbox(
        "Select Subject for Pass/Fail breakdown:",
        options=["Maths", "Science", "English"],
        index=0,
        label_visibility="visible"
    )

    subj_pf = pass_fail_stats[selected_pie_subj]
    pie_data = pd.DataFrame({
        "Status": ["Pass (≥ 40)", "Fail (< 40)"],
        "Count": [subj_pf["Pass"], subj_pf["Fail"]]
    })

    # Donut chart
    fig_pie = px.pie(
        pie_data,
        names="Status",
        values="Count",
        hole=0.5,
        color="Status",
        color_discrete_map={
            "Pass (≥ 40)": "#10b981",
            "Fail (< 40)": "#ef4444"
        }
    )
    fig_pie.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#ffffff', width=2))
    )
    fig_pie.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height=320
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ------------------------------------------------------------------------------
# Grade Distribution Overview
# ------------------------------------------------------------------------------
if not processed_df.empty:
    with st.expander("📊 View Grade Distribution Details", expanded=False):
        grade_order = ["A", "B", "C", "D", "F"]
        grade_counts = processed_df["grade"].value_counts().reindex(grade_order, fill_value=0).reset_index()
        grade_counts.columns = ["Grade", "Number of Students"]
        
        col_g1, col_g2 = st.columns([1, 2])
        with col_g1:
            st.dataframe(grade_counts, hide_index=True, use_container_width=True)
        with col_g2:
            fig_grade = px.bar(
                grade_counts,
                x="Grade",
                y="Number of Students",
                text="Number of Students",
                color="Grade",
                color_discrete_map={
                    "A": "#10b981",
                    "B": "#3b82f6",
                    "C": "#f59e0b",
                    "D": "#f97316",
                    "F": "#ef4444"
                }
            )
            fig_grade.update_traces(textposition='outside')
            fig_grade.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=240,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False
            )
            st.plotly_chart(fig_grade, use_container_width=True)
