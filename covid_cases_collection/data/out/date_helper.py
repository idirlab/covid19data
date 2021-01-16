#!/usr/bin/env python3
import pdb
import csv
import os
import pandas as pd
from os import listdir
from os.path import isfile, join
fpaths = [join(os.getcwd(), f) for f in listdir(os.getcwd())]
csvs = [f for f in fpaths if isfile(f) and '.csv' in f]
dfs = [pd.read_csv(f, sep='\t', header=0) for f in csvs]
def add_year(v: pd.Timestamp):
    d, m, y = v.day, v.month, v.year
    y_new = y + 1
    return pd.Timestamp(day=d, month=m, year=y_new)
for i in range(len(dfs)):
  for c in ['date', 'source_timestamp']:
    dfs[i][c] = pd.to_datetime(dfs[i][c])
  mask = (dfs[i].date < '2020-02-01') & (dfs[i].source_timestamp > '2021-01-01')
  dfs[i].loc[mask, 'date'] = dfs[i].loc[mask, 'date'].map(add_year)
  dfs[i].to_csv(csvs[i], sep="\t", quoting=csv.QUOTE_NONE, index=False)
print('done!')
