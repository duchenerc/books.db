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

LAST_COMMA_FIRST = re.compile(r"[a-z-\.\s']+,[\s,]*[a-z-\.\s]+", re.IGNORECASE)
CONTAINS_AND = re.compile(r"\s(and|as|with|\+)\s", re.IGNORECASE)
DELIMITER = re.compile(r"\sand\s|\swith\s|\&|\sw\/|\+", re.IGNORECASE)

T = r"|".join([
    r"\bJr\.?$",
    r"\bSr\.?$",
    r"\bM\.?D\.?$",
    r"\bDr\.?$",
    r"\bEvangelist$",
    r"\bMrs\.?$",
    r"\bRev\.?$",
    r"\bPh\.?\s?D\.?$",
    r"\bR\.?\s*N\.?$",
    r"\bC\.?\s*N\.?\s*S\.?$",
    r"\bM\.?\s*E\.?$",
    r"\bM\.?\s*A\.?$",
    r"\bA\.?\s*M\.?$",
    r"\bF\.?\s*R\.?\s*P\.?\s*S\.?$",
])

TITLES = re.compile(T, re.IGNORECASE)

def parse_last_comma_first(author):
    return [x.strip(" ,") for x in author.split(",") if len(x.strip(" ,")) > 0]

def is_last_comma_first(author):
    return re.fullmatch(LAST_COMMA_FIRST, author) and not re.search(CONTAINS_AND, author)

def strip_titles(author):
    return re.sub(TITLES, "", author).strip(" ,")

def split_author_line(author_line):
    return [x.strip(" ,") for x in re.split(DELIMITER, author_line) if len(x.strip(" ,")) > 0]

def parse_authors(author_line_):

    author_line = strip_titles(author_line_).strip(" ,")
    # print(author_line)

    # try simple "last, first" format
    if is_last_comma_first(author_line):
        return (parse_last_comma_first(author_line),), ()
    
    authors_processed = []
    authors_lookup = []

    # try separated by "&", "and", or "with"
    if re.search(DELIMITER, author_line):
        authors_raw = [strip_titles(x) for x in split_author_line(author_line)]

        for author_raw in authors_raw:
            if is_last_comma_first(author_raw):
                authors_processed.append(parse_last_comma_first(author_raw))

            else:
                authors_lookup.append(author_raw)
    
    else:
        authors_lookup.append(strip_titles(author_line))
    
    return authors_processed, authors_lookup

def main():
    last_comma_first_matches = []
    unmatched = []

    fails = 0
    total_authors = 0

    mydir = dirname(dirname(abspath(__file__)))

    fin = open(f"{mydir}/inventory.csv", newline="")
    csvin = reader(fin)

    json_out = dict()

    next(csvin) # skip headers

    for entry in csvin:
        author_line = entry[0].strip(" ,")

        if len(author_line) == 0:
            continue
        
        total_authors += 1

        processed_authors, lookup_authors = parse_authors(author_line)
        failed = len(lookup_authors) > 0


        if failed:
            fails += 1

            for author in lookup_authors:
                print(author)

                if author not in json_out.keys():
                    json_out[author] = []


        # else:
        #     for author in processed_authors: print(author)
        #     print(author_line)

    fin.close()

    with open("name_check.json", "w") as fout:
        json.dump(json_out, fout)

    matches = total_authors - fails
    percent_matched = matches / total_authors * 100

    print(f"""
    Matched authors: {matches}
    Total authors: {total_authors}

    Matched: {percent_matched:.2f}%
    """)

if __name__ == "__main__":
    main()
