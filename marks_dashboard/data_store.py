# ==============================================================================
# Layer: Data Access & Persistence Layer (Backend Database & Business Logic)
# ------------------------------------------------------------------------------
# ARCHITECTURAL NOTE:
# This file serves as the "persistence layer" for the Student Marks Dashboard.
# All data storage interactions (reading from and writing to disk) and backend
# validation logic are encapsulated here. Because this layer defines a clean,
# abstracted interface (init_data_store, get_all_students, add_student,
# delete_student, etc.), it could later be swapped for a relational database
# like SQLite or PostgreSQL without changing any code in app.py (the presentation layer).
# ==============================================================================

import os
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd

# Define the path to students.csv relative to this file's location
# This ensures reliable file discovery regardless of current working directory
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE_PATH = BASE_DIR / "students.csv"

# Standard CSV schema columns
CSV_COLUMNS = ["roll_no", "name", "maths", "science", "english"]

# Initial sample records to seed the database on the very first run
SAMPLE_STUDENTS = [
    {
        "roll_no": "101",
        "name": "Aarav Sharma",
        "maths": 95,
        "science": 92,
        "english": 88
    },
    {
        "roll_no": "102",
        "name": "Diya Patel",
        "maths": 82,
        "science": 79,
        "english": 85
    },
    {
        "roll_no": "103",
        "name": "Rohan Verma",
        "maths": 65,
        "science": 68,
        "english": 71
    },
    {
        "roll_no": "104",
        "name": "Ananya Iyer",
        "maths": 45,
        "science": 52,
        "english": 48
    },
    {
        "roll_no": "105",
        "name": "Kabir Khan",
        "maths": 35,
        "science": 38,
        "english": 42
    }
]


def init_data_store() -> Dict[str, Any]:
    """
    Initializes the data store.
    If students.csv does not exist, creates the file with header columns
    and seeds it with 3-5 realistic sample records.
    Returns standard status code dictionary.
    """
    try:
        # Check if the CSV file already exists
        if not CSV_FILE_PATH.exists():
            # Create DataFrame with the sample seed records
            seed_df = pd.DataFrame(SAMPLE_STUDENTS, columns=CSV_COLUMNS)
            # Write out to CSV with headers, avoiding automatic index column
            seed_df.to_csv(CSV_FILE_PATH, index=False)
            return {
                "status_code": 201,  # 201 Created
                "success": True,
                "message": f"Created new persistence store at {CSV_FILE_PATH.name} and seeded with {len(SAMPLE_STUDENTS)} records.",
                "seeded": True
            }
        else:
            # File exists; ensure headers match expected schema
            df = pd.read_csv(CSV_FILE_PATH, dtype={"roll_no": str})
            # Verify columns
            missing_cols = [c for c in CSV_COLUMNS if c not in df.columns]
            if missing_cols:
                # Repair schema if corrupted or empty
                for c in missing_cols:
                    df[c] = 0 if c not in ["roll_no", "name"] else ""
                df.to_csv(CSV_FILE_PATH, index=False)

            return {
                "status_code": 200,  # 200 OK
                "success": True,
                "message": f"Data store connected: {CSV_FILE_PATH.name}",
                "seeded": False
            }
    except Exception as e:
        return {
            "status_code": 500,  # 500 Internal Server Error
            "success": False,
            "message": f"Failed to initialize data store: {str(e)}",
            "seeded": False
        }


def get_all_students() -> Dict[str, Any]:
    """
    Reads all student records from students.csv.
    Returns:
        dict: Standard HTTP-style response containing:
            - status_code: 200 on success, 500 on failure
            - success: boolean
            - data: pandas.DataFrame containing the raw records
            - message: status description
    """
    try:
        # Always make sure the file is initialized before reading
        if not CSV_FILE_PATH.exists():
            init_data_store()

        # Read CSV with string type for roll_no to preserve leading zeroes or alphanumeric codes
        df = pd.read_csv(
            CSV_FILE_PATH,
            dtype={"roll_no": str, "name": str},
            keep_default_na=False
        )

        # Cast marks explicitly to numeric values to prevent type inconsistencies
        for subject in ["maths", "science", "english"]:
            df[subject] = pd.to_numeric(df[subject], errors="coerce").fillna(0).astype(int)

        return {
            "status_code": 200,  # 200 OK
            "success": True,
            "message": f"Retrieved {len(df)} student records.",
            "data": df
        }
    except Exception as e:
        # Return empty DataFrame on failure to protect frontend from crashing
        return {
            "status_code": 500,  # 500 Internal Server Error
            "success": False,
            "message": f"Error reading student records: {str(e)}",
            "data": pd.DataFrame(columns=CSV_COLUMNS)
        }


def validate_student_input(name: str, roll_no: str, maths: Any, science: Any, english: Any, existing_rolls=None) -> Tuple[bool, int, str]:
    """
    Validates student payload before saving.
    Rules:
    - Name must be a non-empty string between 2 and 60 characters.
    - Roll number must be a non-empty alphanumeric string.
    - Roll number must be unique (no duplicates allowed).
    - Maths, Science, English must each be numeric and within [0, 100].

    Returns:
        Tuple of (is_valid: bool, status_code: int, error_message: str)
    """
    # 1. Validate student name
    clean_name = str(name).strip() if name is not None else ""
    if not clean_name:
        return False, 400, "Student name cannot be empty."
    if len(clean_name) < 2:
        return False, 400, "Student name must contain at least 2 characters."
    if len(clean_name) > 60:
        return False, 400, "Student name cannot exceed 60 characters."

    # 2. Validate roll number
    clean_roll = str(roll_no).strip() if roll_no is not None else ""
    if not clean_roll:
        return False, 400, "Roll number cannot be empty."
    if len(clean_roll) > 20:
        return False, 400, "Roll number cannot exceed 20 characters."

    # Check for duplicate roll number if existing rolls provided
    if existing_rolls is not None:
        if clean_roll.lower() in [str(r).strip().lower() for r in existing_rolls]:
            return False, 409, f"A student with Roll Number '{clean_roll}' already exists."

    # 3. Validate subject marks (0-100 integer/float)
    marks_map = {"Maths": maths, "Science": science, "English": english}
    for subject_name, mark_val in marks_map.items():
        try:
            val = float(mark_val)
        except (ValueError, TypeError):
            return False, 400, f"{subject_name} marks must be a valid number."

        if val < 0 or val > 100:
            return False, 400, f"{subject_name} marks must be between 0 and 100 (got {mark_val})."

    # All checks passed
    return True, 200, "Validation successful."


def add_student(name: str, roll_no: str, maths: int, science: int, english: int) -> Dict[str, Any]:
    """
    Adds a new student to students.csv after strict backend validation.
    Returns:
        dict: Standard HTTP-style response with status_code (201 on success, 400/409 on error).
    """
    try:
        # Load current data to check for duplicates and ensure file exists
        read_res = get_all_students()
        current_df = read_res["data"]
        existing_rolls = current_df["roll_no"].tolist() if not current_df.empty else []

        # Sanitize inputs
        clean_name = str(name).strip()
        clean_roll = str(roll_no).strip()

        # Run backend input validation
        is_valid, status_code, message = validate_student_input(
            clean_name, clean_roll, maths, science, english, existing_rolls=existing_rolls
        )

        if not is_valid:
            return {
                "status_code": status_code,  # 400 Bad Request or 409 Conflict
                "success": False,
                "message": message,
                "data": None
            }

        # Prepare new row dictionary
        new_student = {
            "roll_no": clean_roll,
            "name": clean_name,
            "maths": int(maths),
            "science": int(science),
            "english": int(english)
        }

        # Append to DataFrame and save back to CSV
        new_row_df = pd.DataFrame([new_student], columns=CSV_COLUMNS)
        updated_df = pd.concat([current_df, new_row_df], ignore_index=True)
        updated_df.to_csv(CSV_FILE_PATH, index=False)

        return {
            "status_code": 201,  # 201 Created
            "success": True,
            "message": f"Student '{clean_name}' (Roll No: {clean_roll}) added successfully!",
            "data": new_student
        }
    except Exception as e:
        return {
            "status_code": 500,  # 500 Internal Server Error
            "success": False,
            "message": f"Failed to save student record: {str(e)}",
            "data": None
        }


def delete_student(roll_no: str) -> Dict[str, Any]:
    """
    Stretch Goal Feature:
    Deletes a student record by their unique roll number.
    Returns:
        dict: Standard HTTP-style response:
            - 200 OK: Student found and deleted
            - 404 Not Found: Roll number does not exist
            - 500 Internal Server Error: IO failure
    """
    try:
        clean_roll = str(roll_no).strip()
        if not clean_roll:
            return {
                "status_code": 400,  # 400 Bad Request
                "success": False,
                "message": "Roll number to delete cannot be empty."
            }

        read_res = get_all_students()
        current_df = read_res["data"]

        if current_df.empty:
            return {
                "status_code": 404,  # 404 Not Found
                "success": False,
                "message": "No students found in the database to delete."
            }

        # Check if roll number exists
        match = current_df[current_df["roll_no"].astype(str) == clean_roll]
        if match.empty:
            return {
                "status_code": 404,  # 404 Not Found
                "success": False,
                "message": f"Student with Roll Number '{clean_roll}' was not found."
            }

        student_name = match.iloc[0]["name"]

        # Filter out the student to delete
        updated_df = current_df[current_df["roll_no"].astype(str) != clean_roll]
        updated_df.to_csv(CSV_FILE_PATH, index=False)

        return {
            "status_code": 200,  # 200 OK
            "success": True,
            "message": f"Successfully deleted student '{student_name}' (Roll No: {clean_roll})."
        }
    except Exception as e:
        return {
            "status_code": 500,
            "success": False,
            "message": f"Error deleting student: {str(e)}"
        }


def assign_grade(average: float) -> str:
    """
    Helper function to calculate letter grade according to requirements:
    - A >= 90
    - B >= 75 (and < 90)
    - C >= 60 (and < 75)
    - D >= 40 (and < 60)
    - F < 40
    """
    if average >= 90:
        return "A"
    elif average >= 75:
        return "B"
    elif average >= 60:
        return "C"
    elif average >= 40:
        return "D"
    else:
        return "F"


def compute_student_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes computed columns (Total, Average, Grade) for the table,
    identifies the class topper, and compiles summary analytics for charts.
    """
    if df.empty:
        return {
            "processed_df": pd.DataFrame(columns=CSV_COLUMNS + ["total", "average", "grade"]),
            "topper": None,
            "subject_averages": {"Maths": 0.0, "Science": 0.0, "English": 0.0},
            "pass_fail_stats": {"Maths": {"Pass": 0, "Fail": 0}, "Science": {"Pass": 0, "Fail": 0}, "English": {"Pass": 0, "Fail": 0}},
            "overall_stats": {"total_students": 0, "class_average": 0.0, "overall_pass_rate": 0.0}
        }

    # Create a working copy to avoid mutating source
    calc_df = df.copy()

    # Calculate Total marks across the three subjects (out of 300)
    calc_df["total"] = calc_df["maths"] + calc_df["science"] + calc_df["english"]

    # Calculate Average marks (out of 100), rounded to 2 decimal places
    calc_df["average"] = (calc_df["total"] / 3.0).round(2)

    # Calculate Grade based on Average score
    calc_df["grade"] = calc_df["average"].apply(assign_grade)

    # Class Topper: student with highest total marks
    max_total = calc_df["total"].max()
    toppers = calc_df[calc_df["total"] == max_total]
    primary_topper = toppers.iloc[0].to_dict() if not toppers.empty else None

    # Subject-wise average marks
    maths_avg = round(float(calc_df["maths"].mean()), 2)
    science_avg = round(float(calc_df["science"].mean()), 2)
    english_avg = round(float(calc_df["english"].mean()), 2)

    # Pass/Fail stats per subject (Passing threshold is >= 40 marks)
    PASS_MARK = 40
    pass_fail = {
        "Maths": {
            "Pass": int((calc_df["maths"] >= PASS_MARK).sum()),
            "Fail": int((calc_df["maths"] < PASS_MARK).sum())
        },
        "Science": {
            "Pass": int((calc_df["science"] >= PASS_MARK).sum()),
            "Fail": int((calc_df["science"] < PASS_MARK).sum())
        },
        "English": {
            "Pass": int((calc_df["english"] >= PASS_MARK).sum()),
            "Fail": int((calc_df["english"] < PASS_MARK).sum())
        }
    }

    # Overall passing (passed if all three subjects >= 40)
    passed_all = (
        (calc_df["maths"] >= PASS_MARK) &
        (calc_df["science"] >= PASS_MARK) &
        (calc_df["english"] >= PASS_MARK)
    ).sum()
    overall_pass_rate = round((passed_all / len(calc_df)) * 100, 1)

    return {
        "processed_df": calc_df,
        "topper": primary_topper,
        "all_toppers": toppers.to_dict(orient="records"),
        "subject_averages": {
            "Maths": maths_avg,
            "Science": science_avg,
            "English": english_avg
        },
        "pass_fail_stats": pass_fail,
        "overall_stats": {
            "total_students": len(calc_df),
            "class_average": round(float(calc_df["average"].mean()), 2),
            "overall_pass_rate": overall_pass_rate
        }
    }
