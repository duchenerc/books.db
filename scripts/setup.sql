PRAGMA 

-- sqlite doesn't take CREATE DATABASE commands,
-- since databases are files

create table authors (
    id integer autoincrement,
    surname text not null,
    given_name text,

    notes text,

    primary key (id asc)
);

create table genres (
    id integer autoincrement,
    genre_name text unique,

    primary key (id asc)
);

create table conditions (
    id integer autoincrement,
    condition text,

    primary key (id asc)
);

create table jackets (
    id integer autoincrement,
    jacket text,

    primary key (id asc)
);

create table bindings (
    id integer autoincrement,
    book_binding text,

    primary key (id asc)
);

create table publishers (
    id integer autoincrement,
    publisher text unique,

    primary key(id asc)
);

create table books (
    id integer autoincrement,
    title not null,

    -- TODO: implement authors column

    publisher_id integer,
    genre_id integer not null,

    jacket_id integer not null,
    grade_id integer not null,
    binding_id integer not null,

    publish_year text not null,
    notes text,

    primary key (id asc),

    foreign key (publisher_id) references publishers (id)
        on delete no action
        on update no action,
    
    foreign key (genre_id) references genres (id)
        on delete no action
        on update no action,
    
    foreign key (jacket_id) references jackets (id)
        on delete no action
        on update no action,
    
    foreign key (grade_id) references conditions (id)
        on delete no action
        on update no action,
    
    foreign key (binding_id) references bindings (id)
        on delete no action
        on update no action,
);
