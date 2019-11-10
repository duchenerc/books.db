create index if not exists author_names
on authors (surname, given_name, id);

create index if not exists book_titles
on books (title, id);

create index if not exists book_publishers
on books (publisher_id, title);

create index if not exists publisher_names
on publishers (publisher, id);

create index if not exists books_titles_publish_years
on books (publish_year, title);

create index if not exists books_missing_data
on books (
    genre_id,
    publisher_id,
    binding_id,
    condition_id,
    jacket_id,
    isbn,
    id,
    title
);
