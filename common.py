import sqlite3
from csv import reader
from os.path import dirname, abspath

from tools.enum_check import parse_binding, parse_condition, parse_jacket
from tools.isbn_check import parse_isbn
from tools.name_check import parse_authors_2, TITLES_NORMALIZED

DATABASE_FILENAME = "books.db"
MYDIR = dirname(abspath(__file__))
SCRIPTS_DIR = f"{MYDIR}/scripts"

INVENTORY = f"{MYDIR}/inventory.csv"

AUTHOR_COL = 0
TITLE_COL = 1
PUBLISHER_COL = 2
CONDITION_COL = 3
JACKET_COL = 4
BINDING_COL = 5
GENRE_COL = 6
ISBN_COL = 7
PUBLISHYEAR_COL = 8
EDITION_COL = 9
PAGES_COL = 10
NOTES_COL = 11

BOOK_INSERT = """
insert into books
(
    title,
    publisher_id,
    genre_id,
    jacket_id,
    condition_id,
    binding_id,
    isbn,
    publish_year,
    book_edition,
    page_count,
    notes,
    id
)
values
(
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?
);
"""

# Returns the sql from a file as a string.
def get_sql_script(filename):
    fin = open(filename)
    sql_script = fin.read()
    fin.close()

    return sql_script

# Connects to the passed db and returns the connection.
def db_connect(filename):
    conn = sqlite3.connect(f"{MYDIR}/{filename}")

    sql_connect = get_sql_script(f"{SCRIPTS_DIR}/connect.sql")

    # execute startup sql to run pragmas
    conn.executescript(sql_connect)

    return conn

# Executes the db setup script
def db_setup(conn):
    sql_setup = get_sql_script(f"{SCRIPTS_DIR}/setup.sql")
    c = conn.cursor()
    c.executescript(sql_setup)
    c.close()

# sets up indexing
def db_index(conn):
    sql_index = get_sql_script(f"{SCRIPTS_DIR}/index.sql")
    c = conn.cursor()
    c.executescript(sql_index)
    c.close()

# Generates a new id every time it is called.
def id_generator():
    counter = 1
    while True:
        yield counter
        counter += 1

def db_exec(conn, sql, *params):
    c = conn.cursor()

    c.execute(sql, params)

    while True:
        row = c.fetchone()

        if row is None:
            break

        yield row

def db_make(conn):

    # Setup csv file open
    fin = open(INVENTORY)
    csvin = reader(fin)

    # Cache stored values
    genres_store = [None]
    jackets_store = [None]
    conditions_store = [None]
    bindings_store = [None]
    publishers_store = [None]

    # make id generators
    genre_idgen = id_generator()
    condition_idgen = id_generator()
    jacket_idgen = id_generator()
    binding_idgen = id_generator()
    publisher_idgen = id_generator()

    book_idgen = id_generator()
    author_idgen = id_generator()

    # insert all titles into db ahead of time
    for title in TITLES_NORMALIZED:
        conn.execute("insert into titles values (NULL, ?);", (title,))

    next(csvin) # skip headers

    for entry in csvin:

        # if row empty, fast continue
        if len(entry[TITLE_COL]) == 0:
            continue

        c = conn.cursor()

        # get column data
        genre = entry[GENRE_COL]
        condition = parse_condition(entry[CONDITION_COL])
        jacket = parse_jacket(entry[JACKET_COL])
        binding = parse_binding(entry[BINDING_COL])
        publisher = entry[PUBLISHER_COL] if len(entry[PUBLISHER_COL]) > 0 else None
        publish_year = int(entry[PUBLISHYEAR_COL])

        edition = entry[EDITION_COL]
        page_count = entry[PAGES_COL]
        book_notes = entry[NOTES_COL]

        title = entry[TITLE_COL]

        try:
            isbn = parse_isbn(entry[ISBN_COL])
        except:
            isbn = None

        # store genres, conditions, jackets, bindings, publishers
        if len(genre.strip()) == 0:
            genre = None 

        if genre not in genres_store:
            genre_new_id = next(genre_idgen)
            c.execute("insert into genres values (?, ?);", (genre_new_id, genre))
            genres_store.append(genre)
            conn.commit()
        
        if condition not in conditions_store:
            condition_new_id = next(condition_idgen)
            c.execute("insert into conditions values (?, ?);", (condition_new_id, condition))
            conditions_store.append(condition)
            conn.commit()
        
        if jacket not in jackets_store:
            jacket_new_id = next(jacket_idgen)
            c.execute("insert into jackets values (?, ?);", (jacket_new_id, jacket))
            jackets_store.append(jacket)
            conn.commit()
        
        if binding not in bindings_store:
            binding_new_id = next(binding_idgen)
            c.execute("insert into bindings values (?, ?);", (binding_new_id, binding))
            bindings_store.append(binding)
            conn.commit()
        
        if publisher not in publishers_store:
            publisher_new_id = next(publisher_idgen)
            c.execute("insert into publishers values (?, ?);", (publisher_new_id, publisher))
            publishers_store.append(publisher)
            conn.commit()
        
        # genre_id
        if genre is None:
            genre_id = None
        else:
            c.execute("select id from genres where genre_name = ?;", (genre,))
            genre_id = c.fetchone()[0]
        
        # condition_id
        if condition is None:
            condition_id = None
        else:
            c.execute("select id from conditions where condition = ?;", (condition,))
            condition_id = c.fetchone()[0]

        # jacket_id
        if jacket is None:
            jacket_id = None
        else:
            c.execute("select id from jackets where jacket = ?;", (jacket,))
            jacket_id = c.fetchone()[0]
        
        # binding_id
        if binding is None:
            binding_id = None
        else:
            c.execute("select id from bindings where book_binding = ?;", (binding,))
            binding_id = c.fetchone()[0]
        
        # publisher_id
        if publisher is None:
            publisher_id = None
        else:
            c.execute("select id from publishers where publisher = ?;", (publisher,))
            publisher_id = c.fetchone()[0]
        
        conn.commit()

        # store book
        this_book_id = next(book_idgen)

        c.execute(BOOK_INSERT, (
            title,
            publisher_id,
            genre_id,
            jacket_id,
            condition_id,
            binding_id,
            isbn,
            publish_year,
            edition,
            page_count,
            book_notes,
            this_book_id
        ))
        
        conn.commit()

        # store authors
        authors = parse_authors_2(entry[AUTHOR_COL])
            
        authors_ids = []
        for last, first, titles in authors:
            
            # get author id
            if len(first) == 0:
                c.execute("select id from authors where surname = ? and given_name = NULL;", (last,))
            else:
                c.execute("select id from authors where surname = ? and given_name = ?;", (last, first))

            results = c.fetchall()

            # if the results from that query are nonexistent,
            # then this author is new.
            # insert author
            if len(results) == 0:
                author_id = next(author_idgen)
                c.execute("insert into authors values (?, ?, ?, NULL);", (author_id, last, first))

                title_ids = []

                # store author's titles
                for title in titles:
                    c.execute("select id from titles where title_name = ?;", (title,))
                    title_ids.append(c.fetchone()[0])
                
                for title_id in title_ids:
                    c.execute("insert into authors_titles values (NULL, ?, ?)", (author_id, title_id))
            
            else:
                author_id = results[0][0]
            
            authors_ids.append(author_id)
        
        conn.commit()

        # store books-authors relationship
        for author_id in authors_ids:
            c.execute("insert into books_authors values (NULL, ?, ?);", (this_book_id, author_id))

        conn.commit()
        c.close()

    fin.close()
