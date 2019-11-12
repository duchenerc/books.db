select authors.surname, authors.given_name, count(author_id)
from authors, (
    select lhs.author_id author_id, rhs.author_id coauthor_id
    from books_authors lhs, books_authors rhs
    where lhs.book_id = rhs.book_id and lhs.id != rhs.id
) j
where authors.id = author_id
group by authors.surname, authors.given_name;
