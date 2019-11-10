
from csv import writer
from os.path import dirname, abspath
import sqlite3
import re

from common import *
from query_explain import QUERIES_REPORTS

WHITESPACE = re.compile(r"\s+")

def write_report(conn, cols, query, params, filename):

    fout = open(filename, "w", newline="")
    csvout = writer(fout)

    csvout.writerow(cols)

    c = conn.cursor()

    c.execute(query, params)

    while True:
        row = c.fetchone()

        if row is None:
            break

        csvout.writerow(row)

    fout.close()

def main():

    conn = db_connect(DATABASE_FILENAME)

    write_report(conn,
        ("count", "last name", "first name"),
        QUERIES_REPORTS["authors_book_ct"],
        (),
        f"{MYDIR}/reports/authors_book_count.csv"
    )

    write_report(conn,
        ("count", "publisher"),
        QUERIES_REPORTS["publisher_book_ct"],
        (),
        f"{MYDIR}/reports/publishers_book_count.csv"
    )

    write_report(conn,
        ("book title", "year of publication"),
        QUERIES_REPORTS["new_books"],
        (),
        f"{MYDIR}/reports/new_books.csv"
    )

    write_report(conn,
        ("book id", "book title"),
        QUERIES_REPORTS["books_missing_data"],
        (),
        f"{MYDIR}/reports/books_missing_data.csv"
    )

    conn.close()

if __name__ == "__main__":
    main()
