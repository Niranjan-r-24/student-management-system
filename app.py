import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

st.title("🎓 Student Management System")

response = requests.get(f"{BASE_URL}/students")

if response.status_code == 200:

    students = response.json()

    total_students = len(students)

    ai_students = len([s for s in students if s["course"] == "AI"])

    ds_students = len([s for s in students if s["course"] == "Data Science"])

    average_age = (
        sum(s["age"] for s in students) / total_students
        if total_students > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", total_students)
    col2.metric("AI Students", ai_students)
    col3.metric("Data Science", ds_students)
    col4.metric("Average Age", round(average_age, 2))

menu = st.sidebar.selectbox(
    "Select Option",
    (
        "Add Student",
        "View Students",
        "Search Student",
        "Update Student",
        "Delete Student"
    )
)

if menu == "Add Student":

    st.header("Add Student")

    student_id = st.number_input("Student ID", min_value=1, step=1)

    name = st.text_input("Name")

    age = st.number_input("Age", min_value=18, step=1)

    course = st.text_input("Course")

    email = st.text_input("Email")

    if st.button("Add Student"):

        student = {
            "id": int(student_id),
            "name": name,
            "age": int(age),
            "course": course,
            "email": email
        }

        response = requests.post(
            f"{BASE_URL}/students",
            json=student
        )

        if response.status_code == 200:
            st.success("Student Added Successfully")
        else:
            st.error(response.json()["detail"])

# -----------------------------
# View Students
# -----------------------------
elif menu == "View Students":

    st.header("View All Students")

    response = requests.get(f"{BASE_URL}/students")

    if response.status_code == 200:

        students = response.json()

        if len(students) > 0:
            df = pd.DataFrame(students)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No students found.")

    else:
        st.error("Unable to fetch students.")

# -----------------------------
# Search Student
# -----------------------------
elif menu == "Search Student":

    st.header("Search Student")

    student_id = st.number_input(
        "Enter Student ID",
        min_value=1,
        step=1
    )

    if st.button("Search"):

        response = requests.get(
            f"{BASE_URL}/students/{student_id}"
        )

        if response.status_code == 200:

            student = response.json()

            st.success("Student Found")

            st.write("### Student Details")

            st.write("**ID:**", student["id"])
            st.write("**Name:**", student["name"])
            st.write("**Age:**", student["age"])
            st.write("**Course:**", student["course"])
            st.write("**Email:**", student["email"])

        else:

            st.error("Student Not Found")

# -----------------------------
# Update Student
# -----------------------------
elif menu == "Update Student":

    st.header("Update Student")

    student_id = st.number_input(
        "Enter Student ID",
        min_value=1,
        step=1,
        key="update_id"
    )

    name = st.text_input("New Name")

    age = st.number_input(
        "New Age",
        min_value=18,
        step=1,
        key="update_age"
    )

    course = st.text_input("New Course")

    email = st.text_input("New Email")

    if st.button("Update Student"):

        student = {
            "id": int(student_id),
            "name": name,
            "age": int(age),
            "course": course,
            "email": email
        }

        response = requests.put(
            f"{BASE_URL}/students/{student_id}",
            json=student
        )

        if response.status_code == 200:
            st.success("Student Updated Successfully")
        else:
            st.error(response.json()["detail"])

# -----------------------------
# Delete Student
# -----------------------------
elif menu == "Delete Student":

    st.header("Delete Student")

    student_id = st.number_input(
        "Enter Student ID",
        min_value=1,
        step=1,
        key="delete_id"
    )

    if st.button("Delete Student"):

        response = requests.delete(
            f"{BASE_URL}/students/{student_id}"
        )

        if response.status_code == 200:
            st.success("Student Deleted Successfully")
        else:
            st.error(response.json()["detail"])