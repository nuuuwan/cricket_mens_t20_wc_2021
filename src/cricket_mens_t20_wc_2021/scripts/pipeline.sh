DIR_SRC=src/cricket_mens_t20_wc_2021

open $DIR_SRC/data/wc_agenda.tsv

python3 $DIR_SRC/historical.py
python3 $DIR_SRC/odds.py
python3 $DIR_SRC/simulate.py
