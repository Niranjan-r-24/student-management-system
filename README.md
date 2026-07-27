# 🎓 Student Management System

A beginner-friendly Student Management System built using FastAPI and Streamlit.

## Features

- Add Student
- View Students
- Search Student
- Update Student
- Delete Student

## Technologies Used

- Python
- FastAPI
- Streamlit
- SQLite

## Installation

```bash
pip install -r requirements.txt
```

Run Backend

```bash
uvicorn main:app --reload
```

The first backend startup creates `students.db` and imports the existing
`sample_data.json` records once. Future changes are stored in SQLite.

Run Frontend

```bash
streamlit run app.py
```
