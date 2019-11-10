create index if not exists author_names
on authors (surname, given_name, id);

create index if not exists book_titles
on books (title, id);

create index if not exists book_publishers
on books (publisher_id, title);

create index if not exists publisher_names
on publishers (publisher, id);


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
