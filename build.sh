#!/bin/bash

# get which task we want to do
param=$1
task=${param:-build}

# set project directory
pa02_dir="$HOME/code/pa02"

# clean files
echo "build: cleaning"
rm -f "$pa02_dir/books.db"
rm -f $pa02_dir/reports/*.csv

# run stuff
if [[ "$task" == "build" ]]; then
    echo "build: creating db"
    python3 "$pa02_dir/main.py"

    echo "build: generating reports"
    python3 "$pa02_dir/report.py"

elif [[ "$task" == "explain" ]]; then
    echo "build: generating explanations"
    python3 "$pa02_dir/query_explain.py"

else
    echo "build: nothing to do"

fi
