import json
import sqlite3


def _get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    connection = sqlite3.connect("monitor.db")
    _setup_db(connection)
    return connection


def _setup_db(db: sqlite3.Connection) -> None:
    """Set up the database with required tables."""
    db.execute(
        "CREATE TABLE IF NOT EXISTS experiments (id INTEGER PRIMARY KEY AUTOINCREMENT, experiment_type TEXT, ids TEXT, ai_model TEXT, use_ocr BOOLEAN, override BOOLEAN, qalab_base_url TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"  # noqa: E501
    )
    db.commit()

    db.execute(
        "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, experiment_id INTEGER, datapoint_id TEXT, result TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(experiment_id) REFERENCES experiments(id))"  # noqa: E501
    )
    db.commit()


def create_experiment(  # noqa: PLR0913, PLR0917
    experiment_type: str, ids: list, ai_model: str, use_ocr: bool, override: bool, qalab_base_url: str
) -> None:
    """Create a new experiment entry in the database."""
    db = _get_connection()

    db.execute(
        "INSERT INTO experiments (experiment_type, ids, ai_model, use_ocr, override, qalab_base_url) VALUES (?, ?, ?, ?, ?, ?)",  # noqa: E501
        (experiment_type, json.dumps(ids), ai_model, int(use_ocr), int(override), qalab_base_url),
    )
    db.commit()
    db.close()


def get_latest_experiment() -> tuple | None:
    """Retrieve the latest experiment from the database."""
    db = _get_connection()

    try:
        return db.execute("SELECT * FROM experiments ORDER BY timestamp DESC LIMIT 1").fetchone()
    except sqlite3.Error:
        return None
    finally:
        db.close()


def update_experiment(experiment_id: int, **kwargs) -> None:  # noqa: ANN003
    """Update an existing experiment entry in the database."""
    db = _get_connection()
    fields = ", ".join([f"{key} = ?" for key in kwargs])
    values = list(kwargs.values())
    values.append(experiment_id)

    db.execute(
        f"UPDATE experiments SET {fields} WHERE id = ?",
        values,
    )
    db.commit()
    db.close()


def reset_experiment() -> None:
    """Reset all experiments and results in the database."""
    db = _get_connection()
    db.execute("DELETE FROM experiments")
    db.execute("DELETE FROM results")
    db.commit()
    db.close()


def create_result(experiment_id: str, datapoint_id: str, result: str) -> None:
    """Create a new result entry in the database."""
    db = _get_connection()
    db.execute(
        "INSERT INTO results (experiment_id, datapoint_id, result) VALUES (?, ?, ?)",
        (experiment_id, datapoint_id, result),
    )
    db.commit()
    db.close()


def get_results_by_experiment(experiment_id: str) -> list:
    """Retrieve all results for a given experiment from the database."""
    db = _get_connection()
    results = db.execute("SELECT * FROM results WHERE experiment_id = ?", (experiment_id,)).fetchall()
    db.close()
    return results
