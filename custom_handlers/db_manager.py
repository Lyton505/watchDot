import json
import aiosqlite
from typing import Optional

DB_PATH = "watchdot.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS intern_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site TEXT NOT NULL,
    root_domain TEXT NOT NULL,
    root_domain_v2 TEXT,
    term TEXT NOT NULL,
    email_json TEXT,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(root_domain, term) ON CONFLICT IGNORE
);
"""


async def init_db(db_path: str = DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(SCHEMA)
        await db.commit()
    print("Database initialized.")


async def already_recorded(root_domain: str, term: str, db_path: str = DB_PATH) -> bool:
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(
            "SELECT 1 FROM intern_hits WHERE root_domain=? AND term=? LIMIT 1",
            (root_domain, term),
        ) as cur:
            return (await cur.fetchone()) is not None


async def record_hit(
    site: str,
    root_domain: str,
    root_domain_v2: str,
    term: str,
    email_json: Optional[dict],
    db_path: str = DB_PATH,
) -> bool:
    """Returns True if inserted (i.e., not a duplicate)."""
    payload = json.dumps(email_json) if email_json is not None else None
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute(
            """INSERT OR IGNORE INTO intern_hits
               (site, root_domain, root_domain_v2, term, email_json)
               VALUES (?, ?, ?, ?, ?)""",
            (site, root_domain, root_domain_v2, term, payload),
        )
        await db.commit()
        return cur.rowcount == 1
