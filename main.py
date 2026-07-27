import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from database import get_connection, initialize_database

app = FastAPI(title="Student Management System")


# -------------------------
# Student Model
# -------------------------
class Student(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    age: int = Field(..., gt=17)
    course: str
    email: EmailStr


@app.on_event("startup")
def startup():
    initialize_database()


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
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO students (id, name, age, course, email) VALUES (?, ?, ?, ?, ?)",
                (student.id, student.name, student.age, student.course, student.email),
            )
    except sqlite3.IntegrityError as error:
        message = "Student ID already exists" if "students.id" in str(error) else "Email already exists"
        raise HTTPException(status_code=400, detail=message) from error

    return {
        "message": "Student Added Successfully",
        "student": student
    }


# -------------------------
# View All Students
# -------------------------
@app.get("/students")
def get_students():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, age, course, email FROM students ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


# -------------------------
# Search Student by ID
# -------------------------
@app.get("/students/{student_id}")
def get_student(student_id: int):
    with get_connection() as connection:
        student = connection.execute(
            "SELECT id, name, age, course, email FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()

    if student:
        return dict(student)

    raise HTTPException(
        status_code=404,
        detail="Student Not Found"
    )


# -------------------------
# Update Student
# -------------------------
@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):
    # The ID in the URL identifies the record; it cannot be changed accidentally.
    try:
        with get_connection() as connection:
            result = connection.execute(
                """
                UPDATE students
                SET name = ?, age = ?, course = ?, email = ?
                WHERE id = ?
                """,
                (
                    updated_student.name,
                    updated_student.age,
                    updated_student.course,
                    updated_student.email,
                    student_id,
                ),
            )
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=400, detail="Email already exists") from error

    if result.rowcount:
        return {
            "message": "Student Updated Successfully",
            "student": {**updated_student.model_dump(), "id": student_id},
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
    with get_connection() as connection:
        result = connection.execute("DELETE FROM students WHERE id = ?", (student_id,))

    if result.rowcount:
        return {"message": "Student Deleted Successfully"}

    raise HTTPException(
        status_code=404,
        detail="Student Not Found"
    )
