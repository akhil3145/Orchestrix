"""SQLite-backed candidate history for recruitment intelligence."""

from __future__ import annotations

import datetime as dt
import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    candidate_name TEXT NOT NULL,
    target_role TEXT NOT NULL,
    source_file TEXT,
    ats_score INTEGER NOT NULL,
    recommendation TEXT NOT NULL,
    analysis_json TEXT NOT NULL,
    resume_text TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_candidates_role_score
ON candidates(target_role, ats_score DESC);

CREATE INDEX IF NOT EXISTS idx_candidates_created
ON candidates(created_at DESC);
"""


def _connect() -> sqlite3.Connection:
    db_path = Path(os.getenv("CANDIDATE_DB_PATH", settings.candidate_db_path))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def save_candidate_analysis(analysis: Dict[str, Any], resume_text: str, source_file: str = "") -> int:
    created_at = dt.datetime.now(dt.UTC).isoformat()
    with closing(_connect()) as conn:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO candidates (
                    created_at, candidate_name, target_role, source_file,
                    ats_score, recommendation, analysis_json, resume_text
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    analysis["candidate_name"],
                    analysis["target_role"],
                    source_file,
                    int(analysis["ats_score"]),
                    analysis["recommendation"],
                    json.dumps(analysis, ensure_ascii=False),
                    resume_text,
                ),
            )
            return int(cursor.lastrowid)


def list_candidate_history(limit: int = 50, role: Optional[str] = None) -> List[Dict[str, Any]]:
    query = "SELECT * FROM candidates"
    params: List[Any] = []
    if role:
        query += " WHERE target_role = ?"
        params.append(role)
    query += " ORDER BY ats_score DESC, created_at DESC LIMIT ?"
    params.append(limit)

    with closing(_connect()) as conn:
        rows = conn.execute(query, params).fetchall()

    candidates = []
    for row in rows:
        analysis = json.loads(row["analysis_json"])
        candidates.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "candidate_name": row["candidate_name"],
                "target_role": row["target_role"],
                "source_file": row["source_file"],
                "ats_score": row["ats_score"],
                "recommendation": row["recommendation"],
                "analysis": analysis,
            }
        )
    return candidates


def get_candidate(candidate_id: int) -> Optional[Dict[str, Any]]:
    with closing(_connect()) as conn:
        row = conn.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,)).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "candidate_name": row["candidate_name"],
        "target_role": row["target_role"],
        "source_file": row["source_file"],
        "ats_score": row["ats_score"],
        "recommendation": row["recommendation"],
        "analysis": json.loads(row["analysis_json"]),
        "resume_text": row["resume_text"],
    }


def ranked_candidates(limit: int = 25) -> List[Dict[str, Any]]:
    candidates = list_candidate_history(limit=limit)
    for index, candidate in enumerate(candidates, start=1):
        candidate["rank"] = index
    return candidates
