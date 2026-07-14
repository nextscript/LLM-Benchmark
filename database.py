"""
Database Module: SQLite initialization and all database operations.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "benchmarks.db")


def get_db_path() -> str:
    """Return absolute path to database."""
    return DB_PATH


def migrate_db():
    """Add new columns to existing tables if they are missing."""
    conn = get_connection()
    try:
        for stmt in [
            "ALTER TABLE benchmark_runs ADD COLUMN tokens_per_second REAL DEFAULT 0",
            "ALTER TABLE benchmark_runs ADD COLUMN decoded_tokens INTEGER DEFAULT 0",
            "ALTER TABLE benchmark_runs ADD COLUMN elapsed_seconds REAL",
            "ALTER TABLE benchmark_results ADD COLUMN elapsed_seconds REAL",
            "ALTER TABLE benchmark_results ADD COLUMN format_score REAL DEFAULT 50",
            "ALTER TABLE benchmark_results ADD COLUMN consistency_score REAL DEFAULT 50",
            "ALTER TABLE benchmark_results ADD COLUMN run1_quality_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN run2_quality_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN self_validation_used INTEGER DEFAULT 0",
            # Multi-language coding test columns
            "ALTER TABLE benchmark_results ADD COLUMN prompt_key TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN prompt_category TEXT DEFAULT 'general'",
            "ALTER TABLE benchmark_results ADD COLUMN programming_language TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN programming_language_label TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN language_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN language_rating TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN language_rating_label TEXT",
            # Run ID for grouping results
            "ALTER TABLE benchmark_results ADD COLUMN run_id INTEGER",
            # Engine skill columns
            "ALTER TABLE benchmark_results ADD COLUMN engine_skill TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN engine_skill_label TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN engine_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN engine_rating TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN engine_rating_label TEXT",
            # Songwriting test columns
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_skill TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_skill_label TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_rating TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_rating_label TEXT",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_hook_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_rhyme_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_meter_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_emotion_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_structure_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_originality_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN songwriting_suno_format_score REAL DEFAULT 0",
            "ALTER TABLE benchmark_results ADD COLUMN run_number INTEGER DEFAULT 1",
        ]:
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError:
                pass
        conn.commit()
    finally:
        conn.close()


def get_connection() -> sqlite3.Connection:
    """Establish a new database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they do not exist."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS benchmark_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                model_name TEXT NOT NULL,
                server_url TEXT NOT NULL,
                context_size INTEGER,
                prompt_name TEXT,
                prompt_text TEXT,
                prompt_key TEXT,
                prompt_category TEXT DEFAULT 'general',
                programming_language TEXT,
                programming_language_label TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                prompt_tokens_per_second REAL,
                generation_tokens_per_second REAL,
                total_duration REAL,
                first_token_latency REAL,
                avg_token_latency REAL,
                ram_usage_mb REAL,
                vram_usage_mb REAL,
                quality_score REAL DEFAULT 50,
                stability_score REAL DEFAULT 100,
                context_score REAL DEFAULT 50,
                format_score REAL DEFAULT 50,
                consistency_score REAL DEFAULT 50,
                run1_quality_score REAL DEFAULT 0,
                run2_quality_score REAL DEFAULT 0,
                self_validation_used INTEGER DEFAULT 0,
                language_score REAL DEFAULT 0,
                language_rating TEXT,
                language_rating_label TEXT,
                engine_skill TEXT,
                engine_skill_label TEXT,
                engine_score REAL DEFAULT 0,
                engine_rating TEXT,
                engine_rating_label TEXT,
                songwriting_skill TEXT,
                songwriting_skill_label TEXT,
                songwriting_score REAL DEFAULT 0,
                songwriting_rating TEXT,
                songwriting_rating_label TEXT,
                songwriting_hook_score REAL DEFAULT 0,
                songwriting_rhyme_score REAL DEFAULT 0,
                songwriting_meter_score REAL DEFAULT 0,
                songwriting_emotion_score REAL DEFAULT 0,
                songwriting_structure_score REAL DEFAULT 0,
                songwriting_originality_score REAL DEFAULT 0,
                songwriting_suno_format_score REAL DEFAULT 0,
                final_score REAL,
                status TEXT DEFAULT 'finished',
                error_message TEXT,
                run_id INTEGER,
                run_number INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS benchmark_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                server_url TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'waiting',
                progress INTEGER DEFAULT 0,
                current_step TEXT,
                started_at TEXT,
                finished_at TEXT,
                error_message TEXT
            );
        """)
        conn.commit()
    finally:
        conn.close()


# Model operations
def create_model(name: str, path: Optional[str] = None) -> int:
    """Create a model if needed and return its ID."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT id FROM models WHERE name=? ORDER BY id ASC LIMIT 1", (name,)).fetchone()
        if row:
            return row["id"]

        cursor = conn.execute(
            "INSERT INTO models (name, path, created_at) VALUES (?, ?, ?)",
            (name, path, datetime.utcnow().isoformat())
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_models() -> List[Dict[str, Any]]:
    """Return all models."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM models ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# Benchmark run operations
def create_run(model_name: str, server_url: str) -> int:
    """Create a new benchmark run and return its ID."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO benchmark_runs (model_name, server_url, status, progress, started_at) VALUES (?, ?, 'waiting', 0, ?)",
            (model_name, server_url, datetime.utcnow().isoformat())
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_run_status(run_id: int, status: str, progress: Optional[int] = None,
                      current_step: Optional[str] = None, error_message: Optional[str] = None,
                      tokens_per_second: Optional[float] = None, decoded_tokens: Optional[int] = None):
    """Update the status of a benchmark run."""
    conn = get_connection()
    try:
        if status in ("finished", "failed"):
            now = datetime.utcnow().isoformat()
            row = conn.execute("SELECT started_at FROM benchmark_runs WHERE id=?", (run_id,)).fetchone()
            elapsed_seconds = None
            if row and row["started_at"]:
                try:
                    started = datetime.fromisoformat(row["started_at"].replace("Z", ""))
                    elapsed_seconds = (datetime.utcnow() - started).total_seconds()
                except (ValueError, TypeError):
                    elapsed_seconds = None
            conn.execute(
                "UPDATE benchmark_runs SET status=?, progress=?, current_step=?, finished_at=?, error_message=?, elapsed_seconds=? WHERE id=?",
                (status, progress or 100, current_step, now, error_message, elapsed_seconds, run_id)
            )
        else:
            updates = ["status=?", "progress=?", "current_step=?"]
            values: list = [status, progress or 0, current_step]
            if error_message:
                updates.append("error_message=?")
                values.append(error_message)
            if tokens_per_second is not None:
                updates.append("tokens_per_second=?")
                values.append(tokens_per_second)
            if decoded_tokens is not None:
                updates.append("decoded_tokens=?")
                values.append(decoded_tokens)
            values.append(run_id)
            conn.execute(f"UPDATE benchmark_runs SET {', '.join(updates)} WHERE id=?", values)
        conn.commit()
    finally:
        conn.close()


def get_run(run_id: int) -> Optional[Dict[str, Any]]:
    """Return a benchmark run."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM benchmark_runs WHERE id=?", (run_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_active_run() -> Optional[Dict[str, Any]]:
    """Return the newest benchmark run that is still active."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM benchmark_runs "
            "WHERE status IN ('waiting', 'running') "
            "ORDER BY started_at DESC, id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# Result operations
def create_result(result: Dict[str, Any]) -> int:
    """Save or update a benchmark result for the same model, category, and prompt."""
    conn = get_connection()
    try:
        try:
            conn.execute("ALTER TABLE benchmark_results ADD COLUMN run_number INTEGER DEFAULT 1")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        now = datetime.utcnow().isoformat()
        columns = [
            "model_id", "model_name", "server_url", "context_size", "prompt_name",
            "prompt_text", "prompt_key", "prompt_category",
            "programming_language", "programming_language_label",
            "engine_skill", "engine_skill_label",
            "songwriting_skill", "songwriting_skill_label",
            "prompt_tokens", "completion_tokens", "total_tokens",
            "prompt_tokens_per_second", "generation_tokens_per_second",
            "total_duration", "first_token_latency", "avg_token_latency",
            "ram_usage_mb", "vram_usage_mb", "quality_score", "stability_score",
            "context_score", "format_score", "consistency_score",
            "run1_quality_score", "run2_quality_score", "self_validation_used",
            "language_score", "language_rating", "language_rating_label",
            "engine_score", "engine_rating", "engine_rating_label",
            "songwriting_score", "songwriting_rating", "songwriting_rating_label",
            "songwriting_hook_score", "songwriting_rhyme_score", "songwriting_meter_score",
            "songwriting_emotion_score", "songwriting_structure_score",
            "songwriting_originality_score", "songwriting_suno_format_score",
            "final_score", "status", "error_message", "run_id", "run_number", "created_at",
        ]
        values = [
            result.get("model_id"),
            result["model_name"],
            result["server_url"],
            result.get("context_size"),
            result.get("prompt_name"),
            result.get("prompt_text"),
            result.get("prompt_key"),
            result.get("prompt_category", "general"),
            result.get("programming_language"),
            result.get("programming_language_label"),
            result.get("engine_skill"),
            result.get("engine_skill_label"),
            result.get("songwriting_skill"),
            result.get("songwriting_skill_label"),
            result.get("prompt_tokens"),
            result.get("completion_tokens"),
            result.get("total_tokens"),
            result.get("prompt_tokens_per_second"),
            result.get("generation_tokens_per_second"),
            result.get("total_duration"),
            result.get("first_token_latency"),
            result.get("avg_token_latency"),
            result.get("ram_usage_mb"),
            result.get("vram_usage_mb"),
            result.get("quality_score", 50),
            result.get("stability_score", 100),
            result.get("context_score", 50),
            result.get("format_score", 50),
            result.get("consistency_score", 50),
            result.get("run1_quality_score", 0),
            result.get("run2_quality_score", 0),
            1 if result.get("self_validation_used") else 0,
            result.get("language_score", 0),
            result.get("language_rating"),
            result.get("language_rating_label"),
            result.get("engine_score", 0),
            result.get("engine_rating"),
            result.get("engine_rating_label"),
            result.get("songwriting_score", 0),
            result.get("songwriting_rating"),
            result.get("songwriting_rating_label"),
            result.get("songwriting_hook_score", 0),
            result.get("songwriting_rhyme_score", 0),
            result.get("songwriting_meter_score", 0),
            result.get("songwriting_emotion_score", 0),
            result.get("songwriting_structure_score", 0),
            result.get("songwriting_originality_score", 0),
            result.get("songwriting_suno_format_score", 0),
            result.get("final_score"),
            result.get("status", "finished"),
            result.get("error_message"),
            result.get("run_id"),
            result.get("run_number", 1),
            now,
        ]

        placeholders = ", ".join("?" for _ in columns)
        cursor = conn.execute(
            f"INSERT INTO benchmark_results ({', '.join(columns)}) VALUES ({placeholders})",
            values
        )
        result_id = cursor.lastrowid

        conn.commit()
        return result_id
    finally:
        conn.close()


def get_all_results() -> List[Dict[str, Any]]:
    """Return all results sorted by first place."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT br.*, m.name as model_path, br.elapsed_seconds AS elapsed_seconds "
            "FROM benchmark_results br "
            "LEFT JOIN models m ON br.model_id = m.id "
            "ORDER BY br.final_score DESC, br.generation_tokens_per_second DESC, br.first_token_latency ASC"
        ).fetchall()
        results = [dict(r) for r in rows]
        # Backfill elapsed_seconds from the matching benchmark_run when missing
        run_cache: Dict[int, Any] = {}
        for r in results:
            if r.get("elapsed_seconds") is None and r.get("run_id"):
                rid = r["run_id"]
                if rid not in run_cache:
                    row = conn.execute(
                        "SELECT elapsed_seconds FROM benchmark_runs WHERE id=?", (rid,)
                    ).fetchone()
                    run_cache[rid] = row["elapsed_seconds"] if row else None
                r["elapsed_seconds"] = run_cache[rid]
        # Add ranking place
        for i, r in enumerate(results):
            r["ranking_place"] = i + 1
        return results
    finally:
        conn.close()


def get_result(result_id: int) -> Optional[Dict[str, Any]]:
    """Return a single result."""
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT br.*, m.name as model_path FROM benchmark_results br
            LEFT JOIN models m ON br.model_id = m.id
            WHERE br.id=?
        """, (result_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_result(result_id: int) -> bool:
    """Delete a result."""
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM benchmark_results WHERE id=?", (result_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_result_run(result_id: int) -> bool:
    """Delete the full displayed result group for the result's model."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT model_name FROM benchmark_results WHERE id=?", (result_id,)).fetchone()
        if not row:
            return False

        cursor = conn.execute("DELETE FROM benchmark_results WHERE model_name=?", (row["model_name"],))

        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def update_quality_score(result_id: int, quality_score: float) -> bool:
    """Update the quality score of a result."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE benchmark_results SET quality_score=?, final_score=? WHERE id=?",
            (quality_score, None, result_id)  # final_score is recalculated on next scan
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_language_badges_by_model() -> Dict[str, List[Dict[str, Any]]]:
    """Return language badge data grouped by model.

    Returns dict: {model_name: [{language, language_label, score, rating, rating_label}, ...]}
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT model_name, programming_language, programming_language_label, "
            "AVG(language_score) as avg_score, language_rating, language_rating_label "
            "FROM benchmark_results "
            "WHERE programming_language IS NOT NULL "
            "  AND language_score IS NOT NULL "
            "  AND language_score > 0 "
            "GROUP BY model_name, programming_language "
            "ORDER BY model_name, programming_language"
        ).fetchall()

        badges: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            model = row["model_name"]
            if model not in badges:
                badges[model] = []
            badges[model].append({
                "language": row["programming_language"],
                "language_label": row["programming_language_label"] or row["programming_language"],
                "score": round(row["avg_score"], 1),
                "rating": row["language_rating"],
                "rating_label": row["language_rating_label"],
            })
        return badges
    finally:
        conn.close()


def get_engine_badges_by_model() -> Dict[str, List[Dict[str, Any]]]:
    """Return engine skill badge data grouped by model.

    Returns dict: {model_name: [{engine_skill, engine_skill_label, score, rating, rating_label}, ...]}
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT model_name, engine_skill, engine_skill_label, "
            "AVG(engine_score) as avg_score, engine_rating, engine_rating_label "
            "FROM benchmark_results "
            "WHERE engine_skill IS NOT NULL "
            "  AND engine_score IS NOT NULL "
            "  AND engine_score > 0 "
            "GROUP BY model_name, engine_skill "
            "ORDER BY model_name, engine_skill"
        ).fetchall()

        badges: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            model = row["model_name"]
            if model not in badges:
                badges[model] = []
            badges[model].append({
                "engine_skill": row["engine_skill"],
                "engine_skill_label": row["engine_skill_label"] or row["engine_skill"],
                "score": round(row["avg_score"], 1),
                "rating": row["engine_rating"],
                "rating_label": row["engine_rating_label"],
            })
        return badges
    finally:
        conn.close()


def get_best_coding_model_by_badges() -> Optional[Dict[str, Any]]:
    """Find the model with the most 'good' badges across General, Coding Languages, and Game Engine categories.

    A badge (one per general test, programming language, or engine skill) is
    'good' when the model's average score across all its passes for that
    item is >= 75 - the same rule the badge displays elsewhere in the UI use
    (see getAllLanguageBadges/getAllEngineBadges/getAllGeneralBadges in app.js).
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT model_name, prompt_category, prompt_key, final_score, "
            "programming_language, language_score, engine_skill, engine_score "
            "FROM benchmark_results WHERE status = 'finished'"
        ).fetchall()

        # model_name -> (category, item_key) -> list of scores
        scores: Dict[str, Dict[tuple, list]] = {}
        for row in rows:
            model = row["model_name"]
            model_scores = scores.setdefault(model, {})

            if row["prompt_category"] == "general" and row["prompt_key"] and row["final_score"] is not None:
                model_scores.setdefault(("general", row["prompt_key"]), []).append(row["final_score"])

            if row["programming_language"] and row["language_score"] is not None:
                model_scores.setdefault(("coding", row["programming_language"].lower()), []).append(row["language_score"])

            if row["engine_skill"] and row["engine_score"] is not None:
                model_scores.setdefault(("engine", row["engine_skill"].lower()), []).append(row["engine_score"])

        best: Optional[Dict[str, Any]] = None
        for model, model_scores in scores.items():
            counts = {"general": 0, "coding": 0, "engine": 0}
            for (category, _item), values in model_scores.items():
                if sum(values) / len(values) >= 75:
                    counts[category] += 1

            total_good_badges = counts["general"] + counts["coding"] + counts["engine"]
            if best is None or total_good_badges > best["total_good_badges"]:
                best = {
                    "model_name": model,
                    "total_good_badges": total_good_badges,
                    "general_badges": counts["general"],
                    "coding_badges": counts["coding"],
                    "engine_badges": counts["engine"],
                }

        return best
    finally:
        conn.close()


def get_stats() -> Dict[str, Any]:
    """Return statistics for the dashboard."""
    conn = get_connection()
    try:
        stats = {}
        stats["total_models"] = conn.execute("SELECT COUNT(*) FROM models").fetchone()[0]
        stats["total_benchmarks"] = conn.execute("SELECT COUNT(*) FROM benchmark_results").fetchone()[0]

        row = conn.execute(
            "SELECT model_name, AVG(final_score) AS avg_final_score, COUNT(*) AS test_count "
            "FROM benchmark_results WHERE status='finished' "
            "GROUP BY model_name ORDER BY avg_final_score DESC LIMIT 1"
        ).fetchone()
        stats["best_model"] = dict(row) if row else None

        row = conn.execute(
            "SELECT model_name, AVG(total_duration) AS avg_duration, "
            "AVG(generation_tokens_per_second) AS avg_gen_tps, COUNT(*) AS test_count "
            "FROM benchmark_results WHERE status='finished' "
            "GROUP BY model_name ORDER BY avg_duration ASC LIMIT 1"
        ).fetchone()
        stats["fastest_model"] = dict(row) if row else None

        # Fastest model by total elapsed run time (lowest elapsed_seconds)
        row = conn.execute(
            "SELECT model_name, AVG(elapsed_seconds) AS avg_elapsed, "
            "MIN(elapsed_seconds) AS min_elapsed, COUNT(*) AS test_count "
            "FROM benchmark_results "
            "WHERE status='finished' AND elapsed_seconds IS NOT NULL AND elapsed_seconds > 0 "
            "GROUP BY model_name ORDER BY avg_elapsed ASC LIMIT 1"
        ).fetchone()
        stats["fastest_elapsed_model"] = dict(row) if row else None

        # Get best coding model by badge count
        stats["best_coding_model"] = get_best_coding_model_by_badges()

        row = conn.execute(
            "SELECT * FROM benchmark_results ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        stats["last_benchmark"] = dict(row) if row else None

        row = conn.execute(
            "SELECT * FROM benchmark_results WHERE status='failed' ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        stats["last_error"] = dict(row) if row else None

        return stats
    finally:
        conn.close()
