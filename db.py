"""Shared database connection helper for the library system."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'library.db'


def get_connection(db_path=DB_PATH):
    """Open the library database with foreign keys enforced."""
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn
