#!/usr/bin/env python3
# Extracts ISBNs from text

from csv import reader
from os.path import abspath, dirname
import re

HYPHENS = re.compile(r"[- .]")
SCIENTIFIC = re.compile(r"(\d+)e\+(\d+)", re.IGNORECASE)
ISBN = re.compile(r"\d{10}|\d{13}")
ISBN_X = re.compile(r"\d{9}x", re.IGNORECASE)

INVENTORY = f"{dirname(dirname(abspath(__file__)))}/inventory.csv"
ISBN_COL = 7

NULL_VALS = [
    "no isbn",
    "none",
    "no isbn===",
    "none shown",
    "noisbn",
    "noneshown",
    "noisbn==="
]

# manually resolve some isbns
RESOLVER = {
    "031271741+5":     "0312717415",
    "0517460884x":     "517460884x",
    "0517460884x":     "517460884x",
    "39914210x":       "039914210x",
    "0400009688x":     "400009688x",
    "34+h34455436520": "3434455436520",
    "0671075145x":     "671075145x",
    "0067660157x":     "067660157x",
}

def extract_scientific(num):
    base, exp = re.match(SCIENTIFIC, num).group(1, 2)
    return str(int(base) * 10 ** int(exp))

def parse_isbn(isbn_line):
    isbn = re.sub(HYPHENS, "", isbn_line)

    valid_isbn = ""

    try:
        isbn = int(isbn)
        valid_isbn = str(isbn)

    except:
        if isbn in NULL_VALS:
            valid_isbn = ""
        
        elif re.fullmatch(ISBN_X, isbn):
            valid_isbn = isbn
        
        elif re.match(SCIENTIFIC, isbn):
            isbn = extract_scientific(isbn)
            valid_isbn = isbn
        
        elif isbn in RESOLVER.keys():
            valid_isbn = RESOLVER[isbn]
        
        else:
            raise ValueError(f"invalid isbn_line: {isbn_line}")
    
    return valid_isbn

def main():
    fin = open(INVENTORY, newline="")
    csvin = reader(fin)

    next(csvin) # skip headers

    valid_isbns = []

    for entry in csvin:
        isbn_raw = entry[ISBN_COL]
        isbn_line = str(isbn_raw).strip().lower()

        if len(isbn_line) == 0: continue

        try:
            isbn = parse_isbn(isbn_line)
        
        except ValueError:
            print(isbn_line)

    fin.close()

if __name__ == "__main__":
    main()
