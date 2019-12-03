# Report

For the more complex queries, I nested some queries to reduce the number of columns that need to be joined together. I added some indexes and views as well.

## Author book count

```sql
-- original query
select count(b.title), a.surname, a.given_name
from books as b, authors as a, books_authors
where a.id = books_authors.author_id and b.id = books_authors.book_id
group by a.surname, a.given_name;

-- new query
select count(b.title), a.surname, a.given_name
from (
    select id, title from books
) as b, (
    select id, surname, given_name from authors
) as a, books_authors
where a.id = books_authors.author_id and b.id = books_authors.book_id group by a.surname, a.given_name;
```

```txt
ORIGINAL QUERY PLAN
|--SCAN TABLE books_authors
|--SEARCH TABLE books AS b USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH TABLE authors AS a USING INTEGER PRIMARY KEY (rowid=?)
`--USE TEMP B-TREE FOR GROUP BY

NEW QUERY PLAN
|--SCAN TABLE books_authors
|--SEARCH TABLE books USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH TABLE authors USING INTEGER PRIMARY KEY (rowid=?)
`--USE TEMP B-TREE FOR GROUP BY
```

## Publisher book count

```sql
-- original query
select count(b.title), p.publisher
from books as b, publishers as p
where b.publisher_id = p.id
group by p.publisher;

-- new query
select count(b.title), p.publisher
from (
    select title, publisher_id from books
) b, publishers p
where b.publisher_id = p.id
group by p.publisher;
```

```txt
ORIGINAL QUERY PLAN
|--SCAN TABLE books AS b
|--SEARCH TABLE publishers AS p USING INTEGER PRIMARY KEY (rowid=?)
`--USE TEMP B-TREE FOR GROUP BY

NEW QUERY PLAN
|--SCAN TABLE publishers AS p USING COVERING INDEX publisher_names
`--SEARCH TABLE books USING COVERING INDEX book_publishers (publisher_id=?)
```

## New books

```sql
-- original query
select books.title, books.publish_year
from books
where books.publish_year >= 2000;

-- new query
select title, publish_year
from books_new;
```

```txt
ORIGINAL QUERY PLAN
`--SCAN TABLE books

NEW QUERY PLAN
`--SCAN TABLE books
```

## Books with missing data

```sql
-- original query
select authors.surname, authors.given_name, count(j.coauthor_id)
from authors, (
    select lhs.author_id author_id, rhs.author_id coauthor_id
    from books_authors lhs, books_authors rhs
    where lhs.book_id = rhs.book_id and lhs.id != rhs.id) j
where authors.id = j.author_id
group by authors.surname, authors.given_name;

-- new query
select authors.surname, authors.given_name, j.num_coauthors
from authors, (
    select author_id, count(coauthor_id) num_coauthors
    from author_collaborations
    group by author_id ) j
where authors.id = j.author_id;
```

```txt
ORIGINAL QUERY PLAN
|--SCAN TABLE books_authors AS lhs
|--SEARCH TABLE authors USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH TABLE books_authors AS rhs USING AUTOMATIC COVERING INDEX (book_id=?)
`--USE TEMP B-TREE FOR GROUP BY

NEW QUERY PLAN
|--MATERIALIZE 1
|  |--SCAN TABLE books_authors AS lhs
|  |--SEARCH TABLE books_authors AS rhs USING AUTOMATIC COVERING INDEX (book_id=?)
|  `--USE TEMP B-TREE FOR GROUP BY
|--SCAN SUBQUERY 1 AS j
`--SEARCH TABLE authors USING INTEGER PRIMARY KEY (rowid=?)
```

## Collaborators

I added a new query with fairly high selectivity that counts the number of collaborators a given author has worked with.

```sql
-- unoptimized query
select authors.surname, authors.given_name, count(j.coauthor_id)
from authors, (
    select lhs.author_id author_id, rhs.author_id coauthor_id
    from books_authors lhs, books_authors rhs
    where lhs.book_id = rhs.book_id and lhs.id != rhs.id ) j
where authors.id = j.author_id
group by authors.surname, authors.given_name;

-- optimized query
select authors.surname, authors.given_name, j.num_coauthors
from authors, (
    select author_id, count(coauthor_id) num_coauthors
    from author_collaborations
    group by author_id ) j
where authors.id = j.author_id;
```

```txt
UNOPTIMIZED QUERY PLAN
|--SCAN TABLE books_authors AS lhs
|--SEARCH TABLE authors USING INTEGER PRIMARY KEY (rowid=?)
|--SEARCH TABLE books_authors AS rhs USING AUTOMATIC COVERING INDEX (book_id=?)
`--USE TEMP B-TREE FOR GROUP BY

OPTMIZED QUERY PLAN
|--MATERIALIZE 1
|  |--SCAN TABLE books_authors AS lhs
|  |--SEARCH TABLE books_authors AS rhs USING AUTOMATIC COVERING INDEX (book_id=?)
|  `--USE TEMP B-TREE FOR GROUP BY
|--SCAN SUBQUERY 1 AS j
`--SEARCH TABLE authors USING INTEGER PRIMARY KEY (rowid=?)
```

## Indexes and views

```sql
-- indexes
create index if not exists author_names
on authors (surname, given_name, id);

create index if not exists book_titles
on books (title, id);

create index if not exists book_publishers
on books (publisher_id, title);

create index if not exists publisher_names
on publishers (publisher, id);

-- views
create view if not exists books_new (
    title,
    publish_year
) as
select title, publish_year
from books
where publish_year >= 2000;

create view if not exists books_missing_data (
    id,
    title
) as
select id, title
from books
where genre_id is null
or publisher_id is null
or binding_id is null
or condition_id is null
or jacket_id is null
or isbn is null;

create view if not exists author_collaborations (
    author_id,
    coauthor_id
) as
select lhs.author_id author_id, rhs.author_id coauthor_id
from books_authors lhs, books_authors rhs
where lhs.book_id = rhs.book_id
    and lhs.id != rhs.id;

```

## Benchmarks

One thing I've noticed with benchmarks is that they've been pretty inconsistent, especially with indexes. Sometimes I'll get gains of about 50ms, and other times I'll get losses of 50ms. I'm not exactly sure what's going on here: it could be system load, or it could be my use of SQLite (it only implements BT indexes), or it could be me not creating indexes correctly.

# Use

This project requires Python 3 and SQLite3 to both be installed. Both binaries must be in your `PATH`.

To create the database and its associated reports, run `bash build.sh`. This will do the following:

* Create the database (named `books.db`) in the project directory, with views and indexes
* Parse the data from `inventory.csv` and populate the database with it
* Generate the requested reports as csv files under the `reports` directory

To get query plans and explanations as well as benchmarks, run `bash build.sh explain`. This will do the following:

* Create the database (named `books.db`) in the project directory
* Parse the data from `inventory.csv` and populate the database with it
* Generate the query plan and benchmarks for the old queries
* Optimize the database by adding views and indexes
* Generate the query plan and benchmarks for the optimized queries
* Generate explanations for each query in the `explanations` directory
