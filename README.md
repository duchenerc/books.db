# Report

For the more complex queries, I nested some queries to reduce the number of columns that need to be joined together. I added some indexes and views as well. Detailed explanations and benchmarks can be found in the `explanations` directory.

One thing I've noticed with benchmarks is that they've been pretty inconsistent, especially with indexes. Sometimes I'll get gains of about 50ms, and other times I'll get losses of 50ms. I'm not exactly sure what's going on here: it could be system load, or it could be my use of SQLite (it only implements BT indexes), or it could be me not creating indexes correctly.

# Use

This project requires Python 3 and SQLite3 to both be installed. Both binaries must be in your `PATH`.

To create the database and its associated reports, run `. build.sh`. This will do the following:

* Create the database (named `books.db`) in the project directory, with views and indexes
* Parse the data from `inventory.csv` and populate the database with it
* Generate the requested reports as csv files under the `reports` directory

To get query plans and explanations as well as benchmarks, run `. build.sh explain`. This will do the following:

* Create the database (named `books.db`) in the project directory
* Parse the data from `inventory.csv` and populate the database with it
* Generate the query plan and benchmarks for the old queries
* Optimize the database by adding views and indexes
* Generate the query plan and benchmarks for the optimized queries
* Generate explanations for each query in the `explanations` directory
