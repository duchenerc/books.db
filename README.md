# Report

I chose to use SQLite for this project for these reasons, among others:

* SQLite's use case is similar to that of tools like Excel. There's a certain appeal to having an actual file to sit in the filesystem -- it is very conveient to copy and share the file.
* SQLite has good native integration with the Python language. Python comes with SQLite support baked in through the `sqlite3` module.

The biggest problems that I ran into was how to parse author names. Most author names were in a last-comma-first format, with any titles appearing at the end, but there were a lot of discrepencies. I spent far too much time writing a custom set of regexes that could parse titles straight out of an author string regardless of their position in the string and without leaving anything else behind. Some author names were impossible to parse, so I created some lookup tables and manually formatted about 300 names. I spent over half my time on this assignment on parsing authors alone.

I also had to write a couple smaller parsing functions to reduce the fragmentation of data for categorical fields, such as binding type, jacket type, and condition. I did not write a resolver for genres; I feel that this is best left up to the collector. As such, there is a fair amount of fragmentation in this field.

Finally, ISBNs also required a very minimal parser to get right.

# Database design

In my original design, I had four primary tables: books, authors, genres, and publishers. I also used a fifth table to represent the many-to-many relationship between books and authors.

This significantly changed with this project. I realized that book conditions, jacket conditions, and bindings needed their own tables in order to be BCNF-compliant. In addition, authors can now have-many titles, and titles can belong-to-many authors, so I need another two tables to store titles and their many-to-many relationship with authors.

# Use

This project requires Python 3 and SQLite3 to both be installed.

To create the database from the included `inventory.csv`, run `python3 main.py`. This will create the `books.db` database in the project directory.

To create the requested reports from `books.db`, run `python3 report.py`. The reports will be generated and placed into the `reports` directory.

To interact with `books.db` directly through SQL, run `sqlite3 books.db`. This will open a SQL prompt. To exit, type `.exit`. 
