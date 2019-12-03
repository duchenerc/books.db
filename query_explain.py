
import sqlite3
import re
from sys import argv
from pprint import pprint
from os.path import dirname, abspath
from subprocess import run, PIPE
from time import perf_counter_ns as timer

from common import *

WHITESPACE = re.compile(r"\s+")

# subqueries
BOOK_TITLES = "select id, title from books"
AUTHOR_NAMES = "select id, surname, given_name from authors"
BOOK_TITLES_PUBLISHERS = "select title, publisher_id from books"

BOOKS_AUTHORS_SELF_JOIN_OLD = """
    select lhs.author_id author_id, rhs.author_id coauthor_id
    from books_authors lhs, books_authors rhs
    where lhs.book_id = rhs.book_id and lhs.id != rhs.id
"""

BOOKS_AUTHORS_SELF_JOIN_NEW = """
    select author_id, count(coauthor_id) num_coauthors
    from author_collaborations
    group by author_id
"""

# main report queries
QUERIES_REPORTS = {

    "authors_book_ct": f"""
        select count(b.title), a.surname, a.given_name
        from ({BOOK_TITLES}) as b, ({AUTHOR_NAMES}) as a, books_authors
        where a.id = books_authors.author_id
        and b.id = books_authors.book_id
        group by a.surname, a.given_name;
    """,

    "publisher_book_ct": f"""
        select count(b.title), p.publisher
        from ({BOOK_TITLES_PUBLISHERS}) b, publishers p
        where b.publisher_id = p.id
        group by p.publisher;
    """,

    "new_books": f"""
        select title, publish_year
        from books_new;
    """,

    "books_missing_data": """
        select id, title
        from books_missing_data;
    """,


    # new query for pa03
    "body_count": f"""
        select authors.surname, authors.given_name, j.num_coauthors
        from authors, ({BOOKS_AUTHORS_SELF_JOIN_NEW}) j
        where authors.id = j.author_id;
    """
}

# old (pa02) unoptimized queries
QUERIES_REPORTS_OLD = {
    "authors_book_ct": """
        select count(b.title), a.surname, a.given_name
        from books as b, authors as a, books_authors
        where a.id = books_authors.author_id
        and b.id = books_authors.book_id
        group by a.surname, a.given_name;
    """,

    "publisher_book_ct": """
        select count(b.title), p.publisher
        from books as b, publishers as p
        where b.publisher_id = p.id
        group by p.publisher;
    """,

    "new_books": f"""
        select books.title, books.publish_year
        from books
        where books.publish_year >= 2000;
    """,

    "books_missing_data": """
        select books.id, books.title
        from books
        where books.genre_id is null
        or books.publisher_id is null
        or books.binding_id is null
        or books.condition_id is null
        or books.jacket_id is null
        or books.isbn is null;
    """,

    # new query for pa03
    "body_count": f"""
        select authors.surname, authors.given_name, count(j.coauthor_id)
        from authors, ({BOOKS_AUTHORS_SELF_JOIN_OLD}) j
        where authors.id = j.author_id
        group by authors.surname, authors.given_name;
    """

}

def main():

    conn = db_connect(DATABASE_FILENAME)

    # set up db without indexing
    db_setup(conn)
    db_make(conn)

    plans = dict()
    benchmarks = dict()

    # benchmark old queries
    for query_name, query_old in QUERIES_REPORTS_OLD.items():

        query_clean = re.sub(WHITESPACE, " ", query_old.strip())
        sql = f"explain query plan {query_clean}"

        # store query plans
        # interact with shell
        result = run(["sqlite3", DATABASE_FILENAME, sql], stdout=PIPE)
        plans[query_name, "old"] = result.stdout.decode().strip()

        # store benchmark
        c = conn.cursor()

        start = timer()
        c.executescript(sql)
        stop = timer()
        benchmarks[query_name, "old"] = stop - start

        c.close()


    # now index
    db_index(conn)

    # benchmark new queries
    for query_name, query_new in QUERIES_REPORTS.items():

        query_clean = re.sub(WHITESPACE, " ", query_new.strip())
        sql = f"explain query plan {query_clean}"
        
        # store query plans
        result = run(["sqlite3", DATABASE_FILENAME, sql], stdout=PIPE)
        plans[query_name, "new"] = result.stdout.decode().strip()

        # store benchmark
        c = conn.cursor()

        start = timer()
        c.executescript(sql)
        stop = timer()
        benchmarks[query_name, "new"] = stop - start

        c.close()
    
    # get template explanation
    with open(f"{MYDIR}/tools/plan_dump_template.txt") as tempin:
        dump_template = tempin.read()
    
    # write explanations
    for query_name in QUERIES_REPORTS.keys():
        with open(f"{MYDIR}/explanations/{query_name}.txt", "w") as fout:
            
            query_new = re.sub(WHITESPACE, " ", QUERIES_REPORTS[query_name].strip())
            query_old = re.sub(WHITESPACE, " ", QUERIES_REPORTS_OLD[query_name].strip())

            params = {
                "query_name": query_name,
                "query_old": query_old,
                "query_old_plan": plans[query_name, "old"],
                "query_old_time": benchmarks[query_name, "old"],
                "query_new": query_new,
                "query_new_plan": plans[query_name, "new"],
                "query_new_time": benchmarks[query_name, "new"],
                "diff_time": benchmarks[query_name, "old"] - benchmarks[query_name, "new"]
            }

            fout.writelines(dump_template.format(**params))

            
    conn.close()


if __name__ == "__main__":
    main()
