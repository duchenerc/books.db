import sqlite3
from csv import reader
import json
from os.path import dirname, abspath

DATABASE_FILENAME = "books.db"
MYDIR = dirname(abspath(__file__))

PRAGMAS = {
    "ignore_check_constraints": "0",
    "foreign_keys": "1",
}

PRAGMAS_SCHEMA = {
    "journal_mode": "wal",
    "synchronous": "0",
    "cache_size": -1 * 64000
}

def db_setup(conn):
    c = conn.cursor()

    c.executescript(f"{MYDIR}/scripts/setup.sql")

def main():
    database_path = f"{MYDIR}/{DATABASE_FILENAME}"
    conn = sqlite3.connect(database_path)

    for pragma, val in PRAGMAS.items():
        conn.execute(f"PRAGMA {pragma} = {val}")

    db_setup(conn)

if __name__ == "__main__":
    main()
