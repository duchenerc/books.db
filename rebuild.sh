
# set project directory
pa02_dir="$HOME/code/pa02"

# clean files
rm -f "$pa02_dir/books.db"
rm -f $pa02_dir/reports/*.csv

# run stuff
python3 "$pa02_dir/main.py"
python3 "$pa02_dir/report.py"
