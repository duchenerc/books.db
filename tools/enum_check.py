from csv import reader
import re

CONDITION_COL = 3
JACKET_COL = 4
BINDING_COL = 5
GENRE_COL = 6


def parse_condition(condition_line):
    condition = condition_line.strip().lower()

    if len(condition) == 0:
        return "very good"

    elif condition == "poor, very poor":
        return "very poor"
    
    elif condition == "fine":
        return "fair"
    
    elif condition == "new":
        return "as new"
    
    else:
        return condition

def parse_jacket(jacket_line):
    jacket = jacket_line.strip().lower()

    if len(jacket) == 0:
        return "no jacket"
    
    elif jacket == "no":
        return "no jacket"

    else:
        return jacket    

def parse_binding(binding_line):
    return binding_line.strip().lower()

def main():
    from isbn_check import INVENTORY

    fin = open(INVENTORY, newline="")
    csvin = reader(fin)

    next(csvin) # skip headers

    conditions_db = []
    jackets_db = []
    bindings_db = []
    genres_db = dict()

    for entry in csvin:
        condition_line = entry[CONDITION_COL]
        jacket_line = entry[JACKET_COL]
        binding_line = entry[BINDING_COL]
        genre = entry[GENRE_COL].strip().lower()

        condition = parse_condition(condition_line)
        jacket = parse_jacket(jacket_line)
        binding = parse_binding(binding_line)
        
        # TODO: handle genres
        if len(genre) == 0:
            genre = "__unknown__"
        

        if condition not in conditions_db:
            conditions_db.append(condition)

        if jacket not in jackets_db:
            jackets_db.append(jacket)

        if binding not in bindings_db:
            bindings_db.append(binding)

        if genre not in genres_db:
            genres_db[genre] = 1
        
        else:
            genres_db[genre] += 1


    fin.close()
    
    for condition in conditions_db: print(condition)
    print()

    for jacket in jackets_db: print(jacket)
    print()

    for binding in bindings_db: print(binding)
    print()

    for genre, count in genres_db.items(): print(f"{genre} ({count})")
    print()


if __name__ == "__main__":
    main()
