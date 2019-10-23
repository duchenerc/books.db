
from csv import writer
from os.path import dirname, abspath
import sqlite3

MYDIR = dirname(abspath(__file__))

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

    conn = sqlite3.connect(f"{MYDIR}/books.db")

    # write reports
    query_authors_book_ct = """
    select count(books.title), authors.surname, authors.given_name
    from books, authors, books_authors
    where authors.id = books_authors.author_id
    and books.id = books_authors.book_id
    group by authors.surname, authors.given_name;
    """

    query_publishers_book_ct = """
    select count(books.title), publishers.publisher
    from books, publishers
    where books.publisher_id = publishers.id
    group by publishers.publisher
    """

    query_new_books = """
    select books.title, books.publish_year
    from books
    where books.publish_year >= 2000
    """

    query_books_missing_data = """
    select books.id, books.title
    from books
    where books.genre_id is null
    or books.publisher_id is null
    or books.binding_id is null
    or books.condition_id is null
    or books.jacket_id is null
    or books.isbn is null;
    """

    write_report(conn,
        ("count", "last name", "first name"),
        query_authors_book_ct,
        (),
        f"{MYDIR}/reports/authors_book_count.csv"
    )

    write_report(conn,
        ("count", "publisher"),
        query_publishers_book_ct,
        (),
        f"{MYDIR}/reports/publishers_book_count.csv"
    )

    write_report(conn,
        ("book title", "year of publication"),
        query_new_books,
        (),
        f"{MYDIR}/reports/new_books.csv"
    )

    write_report(conn,
        ("book id", "book title"),
        query_books_missing_data,
        (),
        f"{MYDIR}/reports/books_missing_data.csv"
    )

if __name__ == "__main__":
    main()
