"""What lives on the user's machine: the results log and the activation key, both under ~/.seoagent."""
from __future__ import annotations

import json
import os
import sqlite3
import time
from typing import Optional

from .models import JobResult

HOME = os.environ.get("SEOAGENT_HOME", os.path.join(os.path.expanduser("~"), ".seoagent"))
FREE_LINKS = 50


def _config_path() -> str:
    return os.path.join(HOME, "config.json")


def read_config() -> dict:
    try:
        with open(_config_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def write_config(**kv) -> dict:
    os.makedirs(HOME, exist_ok=True)
    cfg = {**read_config(), **kv}
    with open(_config_path(), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return cfg


class Results:
    def __init__(self, path: Optional[str] = None):
        self.path = path or os.path.join(HOME, "results.db")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS results(
            id INTEGER PRIMARY KEY, created REAL, slug TEXT, target_url TEXT, anchor_text TEXT, status TEXT,
            live_url TEXT, proof_path TEXT, notes TEXT)""")
        self.db.commit()

    def save(self, r: JobResult) -> int:
        cur = self.db.execute("INSERT INTO results(created,slug,target_url,anchor_text,status,live_url,proof_path,notes) VALUES(?,?,?,?,?,?,?,?)",
                              (time.time(), r.slug, r.target_url, r.anchor_text, r.status, r.live_url, r.proof_path, r.notes))
        self.db.commit()
        return int(cur.lastrowid)

    def all(self, limit: int = 200) -> list[dict]:
        cols = ["id", "created", "slug", "target_url", "anchor_text", "status", "live_url", "proof_path", "notes"]
        rows = self.db.execute(f"SELECT {','.join(cols)} FROM results ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(zip(cols, r)) for r in rows]

    def placed(self) -> int:
        return int(self.db.execute("SELECT COUNT(*) FROM results WHERE status='placed'").fetchone()[0])

    def placed_on(self, slug: str, target_url: str) -> bool:
        return bool(self.db.execute("SELECT 1 FROM results WHERE slug=? AND target_url=? AND status='placed' LIMIT 1", (slug, target_url)).fetchone())
