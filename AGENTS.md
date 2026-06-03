# Repository Guidelines

## Project Structure & Module Organization

This repository is a Flask-based robot inventory control application. The main entry point is `run.py`; application setup lives in `app/__init__.py`. Core backend modules are under `app/`, including robot control and OpenCV/RTSP camera capture. Flask routes are in `app/routes.py`, `app/routes1.py`, and `app/routes_videos.py`; database models are in `app/models.py`.

Frontend templates live in `app/templates/`, with JavaScript, CSS, fonts, images, and bundled UI assets in `app/static/`. Runtime SQLite data is stored in `instance/tasks.db`. Alembic/Flask-Migrate files are in `migrations/`. Operational scripts for camera checks, robot startup, kernel handling, services, and log cleanup are in `scripts/`. Project documentation and hardware/API references are in `docs/`.

## Build, Test, and Development Commands

- `python -m venv .venv` and `.venv\Scripts\activate`: create and activate a local Windows virtual environment.
- `pip install -r requirements.txt`: install Flask, SocketIO, SQLAlchemy, OpenCV, and other runtime dependencies.
- `python run.py`: start the development server on `0.0.0.0:5000`.
- `flask db upgrade`: apply database migrations; set `FLASK_APP=run.py` first when needed.
- `python -m compileall app`: quick syntax validation for the application package.

On Linux targets, use the provided shell scripts such as `robot_start.sh`, `robot_restart.sh`, and `scripts/robot_start.sh` for deployment-oriented startup workflows.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation. Keep module names lowercase with underscores, matching existing files such as `robot_control.py` and `opencv_control.py`. Use `snake_case` for functions and variables, `PascalCase` for classes, and uppercase names for constants and configuration keys. Prefer existing Flask patterns: initialize shared extensions in `app/__init__.py`, keep database schema in `app/models.py`, and place route handlers in the route modules.

Keep templates in Jinja-compatible HTML and put page-specific JavaScript in `app/static/js/`. Do not hard-code machine-specific secrets or hardware addresses in route logic; read them through `config.py` and `.env`.

## Testing Guidelines

There is no dedicated test suite in this checkout. For small backend changes, run `python -m compileall app` before committing. For database changes, create a migration under `migrations/versions/` and test `flask db upgrade` against a disposable database when possible. For task execution changes, verify task-log behavior against `instance/tasks.db` and check the UI pages in `app/templates/task-logs.html` and related routes.

## Commit & Pull Request Guidelines

Recent commits mostly follow Conventional Commits, for example `feat: ...`, `fix: ...`, and `refactor: ...`. Use that style and avoid empty messages such as `nomsg`.

Pull requests should include a short problem summary, the implementation approach, validation commands run, and any hardware or environment assumptions. Include screenshots for UI changes and note database migrations, `.env` changes, or operational script changes explicitly.

## Security & Configuration Tips

Configuration is loaded from `.env` via `config.py`. Treat credentials such as admin passwords, FTP credentials, robot IPs, and RTSP camera URLs as environment-specific. Do not commit real production secrets or runtime database snapshots unless they are intentionally scrubbed fixtures.
