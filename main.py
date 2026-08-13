import sqlite3
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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


class AttendanceRecord(BaseModel):
    student_id: int = Field(..., gt=0)
    status: Literal["present", "absent"]


class AttendanceBatch(BaseModel):
    attendance_date: date
    records: list[AttendanceRecord] = Field(..., min_length=1)


@app.on_event("startup")
def startup():
    initialize_database()


# -------------------------
# Home Page
# -------------------------
FRONTEND_FILE = Path(__file__).with_name("frontend.html")


@app.get("/", response_class=FileResponse, include_in_schema=False)
def home():
    return FileResponse(FRONTEND_FILE)


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


# -------------------------
# Attendance
# -------------------------
@app.get("/attendance")
def get_attendance(attendance_date: date | None = None):
    query = """
        SELECT attendance.student_id, students.name, attendance.attendance_date, attendance.status
        FROM attendance
        JOIN students ON students.id = attendance.student_id
    """
    params: tuple[str, ...] = ()
    if attendance_date:
        query += " WHERE attendance.attendance_date = ?"
        params = (attendance_date.isoformat(),)
    query += " ORDER BY attendance.attendance_date DESC, students.name"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [dict(row) for row in rows]


@app.post("/attendance")
def save_attendance(batch: AttendanceBatch):
    student_ids = {record.student_id for record in batch.records}
    with get_connection() as connection:
        rows = connection.execute("SELECT id FROM students").fetchall()
        found_ids = {row["id"] for row in rows}
        if found_ids != student_ids:
            raise HTTPException(status_code=404, detail="One or more students were not found")

        connection.executemany(
            """
            INSERT INTO attendance (student_id, attendance_date, status)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, attendance_date) DO UPDATE SET status = excluded.status
            """,
            [
                (record.student_id, batch.attendance_date.isoformat(), record.status)
                for record in batch.records
            ],
        )

    return {"message": "Attendance saved successfully", "records_saved": len(batch.records)}
