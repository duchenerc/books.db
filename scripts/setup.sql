-- sqlite doesn't take CREATE DATABASE commands,
-- since databases are files

create table if not exists authors (
    id integer
    constraint authors_key primary key autoincrement,

    surname text not null,
    given_name text,

    notes text
);

create table if not exists genres (
    id integer
    constraint genres_key primary key autoincrement,

    genre_name text unique
);

create table if not exists conditions (
    id integer
    constraint conditions_key primary key autoincrement,

    condition text
);

create table if not exists jackets (
    id integer
    constraint jackets_key primary key autoincrement,

    jacket text unique
);

create table if not exists bindings (
    id integer
    constraint bindings_key primary key autoincrement,

    book_binding text unique
);

create table if not exists publishers (
    id integer
    constraint publishers_key primary key autoincrement,

    publisher text unique
);

create table if not exists books (
    id integer
    constraint books_key primary key autoincrement,

    title not null,

    publisher_id integer,
    genre_id integer,

    jacket_id integer,
    condition_id integer,
    binding_id integer,

    isbn text,
    publish_year integer,
    book_edition text,
    page_count integer,
    notes text,

    foreign key (publisher_id) references publishers (id)
        on delete no action
        on update no action,
    
    foreign key (genre_id) references genres (id)
        on delete no action
        on update no action,
    
    foreign key (jacket_id) references jackets (id)
        on delete no action
        on update no action,
    
    foreign key (condition_id) references conditions (id)
        on delete no action
        on update no action,
    
    foreign key (binding_id) references bindings (id)
        on delete no action
        on update no action
);

create table if not exists books_authors (
    id integer
    constraint books_authors_key primary key autoincrement,

    book_id integer not null,
    author_id integer not null,

    foreign key (book_id) references books (id)
        on delete no action
        on update no action,
    
    foreign key (author_id) references authors (id)
        on delete no action
        on update no action
);

create table if not exists titles (
    id integer
    constraint titles_key primary key autoincrement,

    title_name text
);

create table if not exists authors_titles (
    id integer
    constraint authors_titles_key primary key autoincrement,

    author_id integer not null,
    title_id integer not null,

    foreign key (author_id) references authors (id)
        on delete no action
        on update no action,
    
    foreign key (title_id) references titles (id)
        on delete no action
        on update no action
);
