from pathlib import Path

content = '''"""
Database layer for the Library Management System.

Uses SQLite, which stores data in a local file and needs no separate server.

Run from the project root:
    python database.py

Import from other modules:
    from database import get_connection, get_db, init_db
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "library.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection and enable SQLite foreign-key enforcement."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """Commit changes on success; roll them back if an error occurs."""
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT UNIQUE,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    publisher TEXT,
    publication_year INTEGER CHECK (
        publication_year IS NULL OR publication_year BETWEEN 0 AND 9999
    ),
    category TEXT,
    total_copies INTEGER NOT NULL DEFAULT 1 CHECK (total_copies >= 0),
    available_copies INTEGER NOT NULL DEFAULT 1 CHECK (
        available_copies >= 0 AND available_copies <= total_copies
    ),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_code TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    loan_date TEXT NOT NULL DEFAULT (date('now')),
    due_date TEXT NOT NULL,
    returned_date TEXT,
    status TEXT NOT NULL DEFAULT 'borrowed'
        CHECK (status IN ('borrowed', 'returned', 'lost')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE RESTRICT,
    CHECK (due_date >= loan_date),
    CHECK (returned_date IS NULL OR returned_date >= loan_date),
    CHECK (
        (status = 'borrowed' AND returned_date IS NULL)
        OR (status = 'returned' AND returned_date IS NOT NULL)
        OR status = 'lost'
    )
);

CREATE TABLE IF NOT EXISTS fines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL UNIQUE,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    reason TEXT NOT NULL DEFAULT 'Overdue return',
    assessed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS fine_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fine_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    payment_method TEXT,
    reference TEXT,
    paid_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fine_id) REFERENCES fines(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_members_name ON members(full_name);
CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id);
CREATE INDEX IF NOT EXISTS idx_loans_book ON loans(book_id);
CREATE INDEX IF NOT EXISTS idx_loans_status_due_date ON loans(status, due_date);
CREATE INDEX IF NOT EXISTS idx_fine_payments_fine ON fine_payments(fine_id);
"""


def init_db() -> None:
    """Create the tables and indexes if they do not already exist."""
    with get_db() as connection:
        connection.executescript(SCHEMA)


def get_fine_balance(fine_id: int) -> int:
    """Return the outstanding fine balance in cents (e.g. 1250 means 12.50)."""
    with get_db() as connection:
        row = connection.execute(
            """
            SELECT f.amount_cents - COALESCE(SUM(p.amount_cents), 0) AS balance
            FROM fines AS f
            LEFT JOIN fine_payments AS p ON p.fine_id = f.id
            WHERE f.id = ?
            GROUP BY f.id, f.amount_cents
            """,
            (fine_id,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Fine with id {fine_id} does not exist.")

    balance = row["balance"]
    if balance < 0:
        raise ValueError(f"Payments exceed the assessed amount for fine {fine_id}.")
    return balance


if __name__ == "__main__":
    init_db()
    print(f"Database initialized successfully: {DATABASE_PATH}")
    with get_db() as connection:
        tables = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
    print("Tables created:")
    for table in tables:
        print(f"  - {table['name']}")
'''

path = Path("/mnt/data/database.py")
path.write_text(content, encoding="utf-8")
print(f"Created: {path}")
