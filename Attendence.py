import streamlit as st
import json
import os
import pandas as pd
from datetime import date


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Student Attendance Tracker",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# FILE SETTINGS
# =========================================================

DATA_FILE = "attendance.json"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #666666;
        font-size: 17px;
        margin-bottom: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# JSON FUNCTIONS
# =========================================================

def load_students():

    if not os.path.exists(DATA_FILE):
        return []

    try:

        with open(DATA_FILE, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, FileNotFoundError):

        return []


def save_students(students):

    with open(DATA_FILE, "w") as file:

        json.dump(
            students,
            file,
            indent=4
        )


# =========================================================
# SESSION STATE
# =========================================================

if "students" not in st.session_state:

    st.session_state.students = load_students()


# =========================================================
# HELPER FUNCTION
# =========================================================

def get_next_id():

    if not st.session_state.students:
        return 1

    return max(
        student["id"]
        for student in st.session_state.students
    ) + 1


# =========================================================
# ADD STUDENT
# =========================================================

def add_student(
    name,
    roll_number,
    branch,
    year
):

    new_student = {

        "id": get_next_id(),

        "name": name,

        "roll_number": roll_number,

        "branch": branch,

        "year": year,

        "attendance": []

    }

    st.session_state.students.append(
        new_student
    )

    save_students(
        st.session_state.students
    )


# =========================================================
# MARK ATTENDANCE
# =========================================================

def mark_attendance(
    student_id,
    attendance_date,
    status
):

    for student in st.session_state.students:

        if student["id"] == student_id:

            # Check whether attendance already exists
            existing_record = None

            for record in student["attendance"]:

                if record["date"] == attendance_date:

                    existing_record = record
                    break

            if existing_record:

                existing_record["status"] = status

            else:

                student["attendance"].append(
                    {
                        "date": attendance_date,
                        "status": status
                    }
                )

            break

    save_students(
        st.session_state.students
    )


# =========================================================
# ATTENDANCE CALCULATION
# =========================================================

def calculate_attendance(student):

    records = student["attendance"]

    total_classes = len(records)

    if total_classes == 0:

        return 0.0, 0, 0

    present_classes = sum(
        1
        for record in records
        if record["status"] == "Present"
    )

    percentage = (
        present_classes / total_classes
    ) * 100

    return (
        percentage,
        present_classes,
        total_classes
    )


# =========================================================
# PAGE TITLE
# =========================================================

st.markdown(
    '<div class="main-title">'
    '📚 STUDENT ATTENDANCE TRACKER'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Manage student attendance and calculate percentages automatically'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Select a section",
    [
        "Dashboard",
        "Add Student",
        "Mark Attendance",
        "Attendance Records"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.header("📊 Attendance Dashboard")

    students = st.session_state.students

    if len(students) == 0:

        st.info(
            "No students added yet."
        )

    else:

        total_students = len(students)

        total_classes = sum(
            len(student["attendance"])
            for student in students
        )

        total_present = sum(
            sum(
                1
                for record in student["attendance"]
                if record["status"] == "Present"
            )
            for student in students
        )

        if total_classes > 0:

            overall_percentage = (
                total_present /
                total_classes
            ) * 100

        else:

            overall_percentage = 0

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "👨‍🎓 Total Students",
                total_students
            )

        with col2:

            st.metric(
                "📚 Total Attendance Records",
                total_classes
            )

        with col3:

            st.metric(
                "📊 Overall Attendance",
                f"{overall_percentage:.2f}%"
            )

        st.divider()

        st.subheader(
            "Student Attendance Summary"
        )

        summary = []

        for student in students:

            percentage, present, total = (
                calculate_attendance(student)
            )

            summary.append(
                {
                    "Roll Number":
                        student["roll_number"],

                    "Name":
                        student["name"],

                    "Branch":
                        student["branch"],

                    "Year":
                        student["year"],

                    "Present":
                        present,

                    "Total Classes":
                        total,

                    "Attendance %":
                        f"{percentage:.2f}%"
                }
            )

        st.dataframe(
            pd.DataFrame(summary),
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# ADD STUDENT
# =========================================================

elif page == "Add Student":

    st.header("➕ Add Student")

    with st.form("student_form"):

        name = st.text_input(
            "Student Name",
            placeholder="Enter student name"
        )

        roll_number = st.text_input(
            "Roll Number",
            placeholder="Enter roll number"
        )

        branch = st.selectbox(
            "Branch",
            [
                "CSE",
                "ECE",
                "EEE",
                "ME",
                "CE",
                "IT",
                "Other"
            ]
        )

        year = st.selectbox(
            "Year",
            [
                "1st Year",
                "2nd Year",
                "3rd Year",
                "4th Year"
            ]
        )

        submit = st.form_submit_button(
            "➕ Add Student",
            use_container_width=True
        )

        if submit:

            if name.strip() == "":

                st.error(
                    "Please enter the student name."
                )

            elif roll_number.strip() == "":

                st.error(
                    "Please enter the roll number."
                )

            else:

                # Check duplicate roll number

                duplicate = any(
                    student["roll_number"]
                    == roll_number.strip()
                    for student
                    in st.session_state.students
                )

                if duplicate:

                    st.error(
                        "This roll number already exists."
                    )

                else:

                    add_student(
                        name.strip(),
                        roll_number.strip(),
                        branch,
                        year
                    )

                    st.success(
                        "Student added successfully!"
                    )


# =========================================================
# MARK ATTENDANCE
# =========================================================

elif page == "Mark Attendance":

    st.header("📝 Mark Attendance")

    students = st.session_state.students

    if len(students) == 0:

        st.info(
            "Please add students first."
        )

    else:

        student_options = {

            f"{student['roll_number']} - "
            f"{student['name']}":
            student["id"]

            for student in students
        }

        with st.form("attendance_form"):

            selected_student = st.selectbox(
                "Select Student",
                list(student_options.keys())
            )

            attendance_date = st.date_input(
                "Attendance Date",
                value=date.today()
            )

            status = st.radio(
                "Attendance Status",
                [
                    "Present",
                    "Absent"
                ],
                horizontal=True
            )

            submit = st.form_submit_button(
                "💾 Save Attendance",
                use_container_width=True
            )

            if submit:

                student_id = student_options[
                    selected_student
                ]

                mark_attendance(
                    student_id,
                    attendance_date.strftime(
                        "%Y-%m-%d"
                    ),
                    status
                )

                st.success(
                    "Attendance saved successfully!"
                )


# =========================================================
# ATTENDANCE RECORDS
# =========================================================

elif page == "Attendance Records":

    st.header("📋 Attendance Records")

    students = st.session_state.students

    if len(students) == 0:

        st.info(
            "No students available."
        )

    else:

        student_options = {

            f"{student['roll_number']} - "
            f"{student['name']}":
            student["id"]

            for student in students
        }

        selected_student = st.selectbox(
            "Select Student",
            list(student_options.keys())
        )

        selected_id = student_options[
            selected_student
        ]

        selected = next(
            student
            for student in students
            if student["id"] == selected_id
        )

        percentage, present, total = (
            calculate_attendance(selected)
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Present",
                present
            )

        with col2:

            st.metric(
                "Total Classes",
                total
            )

        with col3:

            st.metric(
                "Attendance",
                f"{percentage:.2f}%"
            )

        st.divider()

        if len(selected["attendance"]) == 0:

            st.info(
                "No attendance records found."
            )

        else:

            records = []

            for record in selected["attendance"]:

                records.append(
                    {
                        "Date":
                            record["date"],

                        "Status":
                            record["status"]
                    }
                )

            st.dataframe(
                pd.DataFrame(records),
                use_container_width=True,
                hide_index=True
            )

            # Attendance status

            if percentage >= 75:

                st.success(
                    f"Attendance is {percentage:.2f}%."
                )

            else:

                st.warning(
                    f"Attendance is {percentage:.2f}%. "
                    "Below 75%."
                )