import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Student Management System</title>
        <style>
          :root { color-scheme: dark; }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
            font-family: Inter, ui-sans-serif, system-ui, sans-serif;
            color: #edf4ff;
            background: radial-gradient(circle at top left, #315ac5, transparent 42%), #0b1220;
          }
          main {
            width: min(620px, 100%);
            padding: clamp(32px, 7vw, 56px);
            border: 1px solid rgba(255, 255, 255, .18);
            border-radius: 24px;
            background: rgba(16, 26, 48, .78);
            box-shadow: 0 24px 80px rgba(0, 0, 0, .35);
          }
          .badge {
            display: inline-block;
            padding: 7px 11px;
            border-radius: 999px;
            color: #a7f3d0;
            background: rgba(16, 185, 129, .15);
            font-size: .82rem;
            font-weight: 700;
            letter-spacing: .05em;
            text-transform: uppercase;
          }
          h1 { margin: 20px 0 12px; font-size: clamp(2rem, 6vw, 3.5rem); line-height: 1.04; }
          p { margin: 0; color: #c3d1e8; font-size: 1.06rem; line-height: 1.65; }
          a {
            display: inline-block;
            margin-top: 30px;
            padding: 13px 18px;
            border-radius: 10px;
            color: #071221;
            background: #79d7ff;
            font-weight: 750;
            text-decoration: none;
          }
          a:hover { background: #b1e8ff; }
        </style>
      </head>
      <body>
        <main>
          <span class="badge">API online</span>
          <h1>Student Management System</h1>
          <p>Your API is running and ready to manage student records.</p>
          <a href="/docs">Open API documentation &rarr;</a>
        </main>
      </body>
    </html>
    """


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
