create index if not exists author_names
on authors (surname, given_name);

create index if not exists book_titles
on books (title);

create index if not exists publisher_names
on publishers (publisher);

create unique index if not exists author_ids
on authors (id);

create unique index if not exists book_ids
on books (id);

create unique index if not exists publisher_ids
on publishers (id);

create index if not exists books_publish_years
on books (publish_year);

create index if not exists books_titles_publish_years
on books (title, publish_year);
