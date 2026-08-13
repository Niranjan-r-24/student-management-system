"""Attendance persistence tests using an isolated SQLite database."""

import tempfile
import unittest
from pathlib import Path

import database


class AttendanceDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.original_database_file = database.DATABASE_FILE
        self.original_legacy_data_file = database.LEGACY_DATA_FILE
        database.DATABASE_FILE = Path(self.directory.name) / "test_students.db"
        database.LEGACY_DATA_FILE = Path(self.directory.name) / "missing.json"
        database.initialize_database()

    def tearDown(self):
        database.DATABASE_FILE = self.original_database_file
        database.LEGACY_DATA_FILE = self.original_legacy_data_file
        self.directory.cleanup()

    def test_attendance_is_saved_and_deleted_with_student(self):
        with database.get_connection() as connection:
            connection.execute(
                "INSERT INTO students (id, name, age, course, email) VALUES (?, ?, ?, ?, ?)",
                (1, "Ada Lovelace", 20, "AI", "ada@example.com"),
            )
            connection.execute(
                "INSERT INTO attendance (student_id, attendance_date, status) VALUES (?, ?, ?)",
                (1, "2026-08-13", "present"),
            )
            connection.execute("DELETE FROM students WHERE id = ?", (1,))
            remaining = connection.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]

        self.assertEqual(remaining, 0)


if __name__ == "__main__":
    unittest.main()
