import sqlite3
from csv import reader
import json
from os.path import dirname, abspath

from tools.enum_check import parse_binding, parse_condition, parse_jacket
from tools.isbn_check import parse_isbn
from tools.name_check import parse_authors

DATABASE_FILENAME = "books.db"
MYDIR = dirname(abspath(__file__))
SCRIPTS_DIR = f"{MYDIR}/scripts"


def get_sql_script(filename):
    fin = open(filename)
    sql_script = fin.read()
    fin.close()

    return sql_script

def db_connect(filename):
    conn = sqlite3.connect(f"{MYDIR}/{filename}")

    sql_connect = get_sql_script(f"{SCRIPTS_DIR}/connect.sql")

    # execute startup sql to run pragmas
    conn.executescript(sql_connect)

    return conn

def db_setup(conn):
    sql_setup = get_sql_script(f"{SCRIPTS_DIR}/setup.sql")
    c = conn.cursor()
    c.executescript(sql_setup)
    c.close()

def main():
    conn = db_connect(DATABASE_FILENAME)
    db_setup(conn)


if __name__ == "__main__":
    main()
