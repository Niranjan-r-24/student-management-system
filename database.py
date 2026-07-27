"""SQLite persistence helpers for the Student Management System."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "students.db"
LEGACY_DATA_FILE = BASE_DIR / "sample_data.json"


@contextmanager
def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    """Create the schema and import the previous JSON data once, if present."""
    is_new_database = not DATABASE_FILE.exists()

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                age INTEGER NOT NULL CHECK (age >= 18),
                course TEXT NOT NULL CHECK (length(trim(course)) > 0),
                email TEXT NOT NULL UNIQUE
            )
            """
        )

        if is_new_database and LEGACY_DATA_FILE.exists():
            with LEGACY_DATA_FILE.open(encoding="utf-8") as file:
                students = json.load(file)

            connection.executemany(
                """
                INSERT OR IGNORE INTO students (id, name, age, course, email)
                VALUES (:id, :name, :age, :course, :email)
                """,
                students,
            )
