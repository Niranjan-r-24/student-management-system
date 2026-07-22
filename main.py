from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
import json
import os

app = FastAPI(title="Student Management System")

# Change the file name here
DATA_FILE = "sample_data.json"


# -------------------------
# Student Model
# -------------------------
class Student(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=17)
    course: str
    email: EmailStr


# -------------------------
# Load Data
# -------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []


# -------------------------
# Save Data
# -------------------------
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# -------------------------
# Home Page
# -------------------------
@app.get("/")
def home():
    return {
        "message": "Welcome to Student Management System API"
    }


# -------------------------
# Add Student
# -------------------------
@app.post("/students")
def add_student(student: Student):
    students = load_data()

    # Check if ID already exists
    for s in students:
        if s["id"] == student.id:
            raise HTTPException(
                status_code=400,
                detail="Student ID already exists"
            )

    students.append(student.model_dump())
    save_data(students)

    return {
        "message": "Student Added Successfully",
        "student": student
    }


# -------------------------
# View All Students
# -------------------------
@app.get("/students")
def get_students():
    return load_data()


# -------------------------
# Search Student by ID
# -------------------------
@app.get("/students/{student_id}")
def get_student(student_id: int):
    students = load_data()

    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(
        status_code=404,
        detail="Student Not Found"
    )


# -------------------------
# Update Student
# -------------------------
@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):
    students = load_data()

    for i, student in enumerate(students):
        if student["id"] == student_id:
            students[i] = updated_student.model_dump()
            save_data(students)

            return {
                "message": "Student Updated Successfully",
                "student": updated_student
            }

    raise HTTPException(
        status_code=404,
        detail="Student Not Found"
    )


# -------------------------
# Delete Student
# -------------------------
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    students = load_data()

    for student in students:
        if student["id"] == student_id:
            students.remove(student)
            save_data(students)

            return {
                "message": "Student Deleted Successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Student Not Found"
    )