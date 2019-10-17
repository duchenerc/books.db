#!/usr/bin/env python3
#
# Name: Ryan Duchene
# Course: CS 5300
#
# This script acts as a testbed for the name handler module.

import json
from csv import reader
import re
from os.path import abspath, dirname

LAST_COMMA_FIRST = re.compile(r"[a-z-\.\s']+,+\s[a-z-\.\s]+", re.IGNORECASE)
CONTAINS_AND = re.compile(r"\s(and|as|with)\s", re.IGNORECASE)
DELIMITER = re.compile(r"\s(?:and|with|\&|w\/)\s", re.IGNORECASE)

T = r"|".join([
    r"Jr\.?",
    r"Sr\.?",
    r"M\.?D\.?",
    r"Dr\.?",
    r"Evangelist",
    r"Mrs\.?",
    r"Rev\.?",
    r"Ph\.?\s?D\.?"
])

TITLES = re.compile(T, re.IGNORECASE)

def parse_last_comma_first(author):
    return tuple([x.strip() for x in author.split(",") if len(x.strip()) > 0])

def is_last_comma_first(author):
    return re.fullmatch(LAST_COMMA_FIRST, author) and not re.search(CONTAINS_AND, author)

def strip_titles(author):
    return re.sub(TITLES, "", author).strip()

def split_author_line(author_line):
    return [x.strip() for x in re.split(DELIMITER, author_line) if len(x.strip()) > 0]

def parse_authors(author_line_):

    author_line = strip_titles(author_line_)

    # try simple "last, first" format
    if is_last_comma_first(author_line):
        return ((parse_last_comma_first(author_line),),), False
    
    authors_processed = []
    authors_lookup = []

    # try separated by "&", "and", or "with"
    if re.search(DELIMITER, author_line):
        authors_raw = split_author_line(author_line)

        for author_raw in authors_raw:
            if is_last_comma_first(author_raw):
                authors_processed.append(parse_last_comma_first(author_raw))

            else:
                authors_lookup.append(author_raw)
    
    else:
        authors_lookup.append(author_line)
    
    return authors_processed, len(authors_lookup) > 0

def main():
    last_comma_first_matches = []
    unmatched = []

    fails = 0
    total_authors = 0

    mydir = dirname(dirname(abspath(__file__)))

    fin = open(f"{mydir}/inventory.csv", newline="")
    csvin = reader(fin)


    next(csvin) # skip headers

    for entry in csvin:
        author_line = entry[0].strip()

        if len(author_line) == 0:
            continue
        
        total_authors += 1

        processed_authors, failed = parse_authors(author_line)

        if failed:
            fails += 1
            for author in processed_authors: print(author)
            print(author_line)
            print()
        # else:
        #     for author in processed_authors: print(author)
        #     print(author_line)

    fin.close()

    matches = total_authors - fails
    percent_matched = matches / total_authors * 100

    print(f"""
    Matched authors: {matches}
    Total authors: {total_authors}

    Matched: {percent_matched:.2f}%
    """)

if __name__ == "__main__":
    main()
