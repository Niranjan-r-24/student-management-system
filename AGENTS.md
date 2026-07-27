# Repository Guidelines

## Project Structure & Module Organization

- `main.py` contains the FastAPI backend and the student CRUD endpoints.
- `database.py` owns SQLite setup, connection handling, and the initial JSON-to-SQLite import.
- `app.py` is the Streamlit user interface and calls the API at `http://127.0.0.1:8000`.
- `sample_data.json` is legacy seed data, imported only when `students.db` is first created.
- `requirements.txt` lists Python dependencies. Runtime data (`students.db`) must not be treated as source code.

Keep API logic in `main.py`, persistence code in `database.py`, and presentation changes in `app.py`. Add tests in a top-level `tests/` directory as the project grows.

## Build, Test, and Development Commands

Create and activate a virtual environment, then install dependencies:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the backend with automatic reload:

```powershell
uvicorn main:app --reload
```

Run the Streamlit interface in another terminal:

```powershell
streamlit run app.py
```

Check API endpoints interactively at `http://127.0.0.1:8000/docs`. Confirm stored records with `GET /students`.

## Coding Style & Naming Conventions

Use Python with four-space indentation, standard library imports first, and clear type-friendly functions. Use `snake_case` for variables and functions, `PascalCase` for Pydantic models (for example, `Student`), and uppercase for module constants (for example, `DATABASE_FILE`). Keep SQL parameterized with `?` placeholders; never build SQL from user input. Return consistent JSON error details through `HTTPException`.

No formatter, linter, or test framework is configured yet. Avoid unrelated formatting changes in feature work.

## Testing Guidelines

Before submitting changes, start the backend and manually exercise create, list, retrieve, update, and delete through `/docs` or Streamlit. Verify that duplicate IDs and duplicate emails return clear errors. For new automated tests, use `pytest`, name files `tests/test_*.py`, and use a temporary SQLite database so tests never modify `students.db`.

## Commit & Pull Request Guidelines

The repository history currently uses a short imperative subject (`Initial Student Management System`). Follow that pattern: `Add student search endpoint` or `Fix duplicate email validation`. Keep commits focused. Pull requests should state the user-visible change, list validation performed, link any related issue, and include screenshots for Streamlit UI changes.
