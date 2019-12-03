from flask import Flask, render_template
from common import db_connect, DATABASE_FILENAME, db_exec

db = db_connect(DATABASE_FILENAME)
app = Flask(__name__)

@app.route("/")
def index():
    c_books = db_exec(db, """
        select b.id, b.title, b.isbn
        from books b
        order by b.title;
    """)

    c_authors = db_exec(db, """
        select ba.book_id, a.id, a.surname, a.given_name
        from books_authors ba, authors a
        where ba.author_id = a.id;
    """)

    books = {x[0]: {"title": x[1], "isbn": x[2]} for x in c_books}

    authors = dict()

    for book_id, author_id, surname, given_name in c_authors:
        if book_id not in authors.keys():
            authors[book_id] = [{
                "id": int(author_id),
                "surname": surname,
                "given_name": given_name
            }]
        
        else:
            authors[book_id].append({
                "id": int(author_id),
                "surname": surname,
                "given_name": given_name
            })

    return render_template("index.html", books=books, authors=authors)

@app.route("/book/<book_id>")
def book(book_id):

    book_query = db_exec(db, """
        select b.title
        from books b
        where b.id = ?;
    """, book_id)

    book_tup = next(book_query)

    return render_template("book.html", book=book_tup)

@app.route("/author")
def index_author():

    authors_query = db_exec(db, """
        select a.id, a.surname, a.given_name
        from authors a
        order by a.surname, a.given_name;
    """)

    authors = {x[0]: { "surname": x[1], "given_name": x[2] } for x in authors_query}

    books_query = db_exec(db, """
        select ba.author_id, b.id, b.title
        from books_authors ba, books b
        where ba.book_id = b.id;
    """)

    books = dict()

    for author_id, book_id, book_title in books_query:
        if author_id not in books.keys():
            books[author_id] = [{
                "id": book_id,
                "title": book_title
            }]
        
        else:
            books[author_id].append({
                "id": book_id,
                "title": book_title
            })

    return render_template("index_author.html", authors=authors, books=books)

@app.route("/author/<author_id>")
def author(author_id):
    author_query = db_exec(db, """
        select a.surname, a.given_name
        from authors a
        where a.id = ?;
    """, author_id)

    author_tup = next(author_query)

    books_query = db_exec(db, """
        select b.id, b.title
        from books b, books_authors ba
        where b.id = ba.book_id
        and ba.author_id = ?;
    """, author_id)

    books = [{"id": x[0], "title": x[1]} for x in books_query]

    return render_template("author.html", author=author_tup, books=books)

@app.route("/genre")
def index_genre():

    genres_query = db_exec(db, """
        select g.id, g.genre_name
        from genres g
        order by g.genre_name;
    """)

    genres = {x[0]: x[1] for x in genres_query}

    return render_template("index_genre.html", genres=genres)

@app.route("/genre/<genre_id>")
def genre(genre_id):

    genre_query = db_exec(db, """
        select g.id, g.genre_name
        from genres g
        where g.id = ?;
    """, genre_id)

    genre_tup = next(genre_query)

    books_query = db_exec(db, """
        select b.id, b.title, a.id, a.surname, a.given_name 
        from books b, authors a, books_authors ba
        where b.genre_id = ?
        and b.id = ba.book_id
        and a.id = ba.author_id;
    """, genre_id)

    books = dict()
    authors = dict()

    for b_id, b_title, a_id, a_surname, a_given_name in books_query:

        author = {
            "id": a_id,
            "surname": a_surname,
            "given_name": a_given_name
        }

        if b_id not in books.keys():
            books[b_id] = b_title
            authors[b_id] = [author]
                
        else:
            authors[b_id].append(author)
    
    return render_template("genre.html", genre=genre_tup, books=books, authors=authors)
