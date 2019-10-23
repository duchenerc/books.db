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

WRITING_AS = re.compile(r"^.*writing as\s*", re.IGNORECASE)

# a list of title patterns
T = [
    r"\bJr\.?", # Jr.
    r"\bSr\.?", # Sr.
    r"\bM\.?D\.?", # M.D.
    r"\bDr\.?(?=[, ]|$)", # Dr.
    r"\bEvangelist", # Evangelist
    r"\bMrs\.?", # Mrs.
    r"\bRev\.?", # Rev.
    r"\bPh\.?\s*D\.?", # Ph.D.
    r"\bR\.?\s*N\.?", # R.N.
    r"\bC\.?\s*N\.?\s*S\.?", #C.N.S.
    r"\bM\.?\s*E\.?(?=[,]|$)", # M.E.
    r"\bM\.?\s*A\.?(?=[,]|$)", # M.A.
    r"\bA\.?\s*M\.?(?=[,]|$)", # A.M.
    r"\bF\.?\s*R\.?\s*P\.?\s*S\.?", # F.R.P.S
    r"\bB\.?\s*S\.?", # B.S.
    r"\bL\.?\s*H\.?\s*D\.?", # L.H.D.
    r"\bLtt\.?\s*D\.?", # Ltt.D.
    r"\bIII", # III
    # r"\bD\.?\s*A\.?(?=[,]|$)", # D.A.
    r"\bD\.?\s*O\.?(?=[,]|$)", # D.O.
    # r"\bC\.?\s*A\.?(?=[,]|$)", # C.A.
    r"\bEd\.?\s*D\.?" # Ed.D.
]

# match any title
TITLES_ANY = re.compile(r"|".join(T), re.IGNORECASE)

# match one title
TITLES_ONE = [re.compile(x, re.IGNORECASE) for x in T]

# normalized titles
# indices correspond to values of TITLES_ONE
TITLES_NORMALIZED = [
    "Jr.",
    "Sr.",
    "M.D.",
    "Dr.",
    "Evangelist",
    "Mrs.",
    "Rev.",
    "Ph.D.",
    "R.N.",
    "C.N.S.",
    "M.E.",
    "M.A.",
    "A.M.",
    "F.R.P.S.",
    "B.S.",
    "L.H.D.",
    "Ltt.D.",
    "III",
    # "D.A.",
    "D.O.",
    # "C.A.",
    "Ed.D."
]

MYDIR = dirname(abspath(__file__))

# resolvers
RESOLVE_NAME = dict()
RESOLVE_LINE = dict()
RESOLVE_LITERAL = dict()

GARBAGE = (
    "Various Others",
    "None Others",
    "Several Other",
    "Various"
)

if len(RESOLVE_LINE.keys()) == 0:
    with open(f"{MYDIR}/author_resolve.json") as fin:
        resolve_json = json.load(fin)

        RESOLVE_NAME = resolve_json["name"]
        RESOLVE_LINE = resolve_json["line"]
        RESOLVE_LITERAL = resolve_json["literal"]


def parse_titles(author):
    titles = re.findall(TITLES_ANY, author)
    new_author = re.sub(TITLES_ANY, "", author)

    return new_author.strip(" ,"), titles

# normalize a title's spacing
def normalize_title(title):
    if title in TITLES_NORMALIZED:
        return title
    
    for i in range(len(TITLES_ONE)):
        if re.fullmatch(TITLES_ONE[i], title):
            return TITLES_NORMALIZED[i]
    
    raise ValueError(f"invalid title '{title}'")

# parse a single author string into a triple
# last, first, titles
def parse_single_author(author_raw):
    author_raw = author_raw.strip(" ,")
    author_titleless, titles = parse_titles(author_raw)

    titles = [normalize_title(x) for x in titles]

    if re.fullmatch(LAST_COMMA_FIRST, author_titleless):
        author_names = [x.strip(" ,") for x in author_titleless.split(",") if len(x.strip(" ,")) > 0]
    
    elif author_titleless in RESOLVE_NAME.keys():
        name = RESOLVE_NAME[author_titleless]
        if "," in name:
            author_names = [x.strip(" ,") for x in name.split(",")]
        else:
            author_names = (name, "")

    else:
        print(author_raw)
        author_names = (author_titleless, "")
    
    return (*author_names, titles)

# split a line of authors into single-author strings
def split_author_line(author_line):
    return [x.strip(" ,") for x in re.split(DELIMITER, author_line) if len(x.strip(" ,")) > 0]

# preprocess authors and remove some garbage
def author_preprocess(author_line):
    new_author_line = re.sub(WRITING_AS, "", author_line)
    return new_author_line.strip(", ")

# second iteration of parse_authors
# takes an author line, returns a list of triples
# last, first, titles
def parse_authors_2(author_line):
    author_line = author_preprocess(author_line)

    if author_line in RESOLVE_LINE.keys():
        authors_raw = RESOLVE_LINE[author_line]
    
    else:
        authors_raw = split_author_line(author_line)

    authors_final = []

    for author_raw in authors_raw:
        if author_raw in RESOLVE_LITERAL:
            author_final = (author_raw, "", "")
        else:
            author_final = parse_single_author(author_raw)

            if author_final[0] in GARBAGE:
                # print("garbage")
                continue

        if len(author_final[1]) == 0:
            # print(author_line)
            # print()
            pass

        authors_final.append(author_final)

    return authors_final

def main():

    mydir = dirname(dirname(abspath(__file__)))
    inventory_filename = f"{mydir}/inventory.csv"

    fin = open(inventory_filename, newline="")
    csvin = reader(fin)

    next(csvin)

    authors = []

    for entry in csvin:
        if len(entry[0]) == 0:
            continue

        authors += parse_authors_2(entry[0])
    
    cant_figure_out = [x for x in authors if len(x[1]) == 0]

    for author in authors: print(author)

    fin.close()

    print(f"Total manual: {len(cant_figure_out)}")

if __name__ == "__main__":
    main()
