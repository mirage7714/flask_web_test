# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 16:28:49 2018

@author: mirag
"""

import sqlite3
import pandas as pd

file = 'd:/downloads/gates.csv'
db_path = 'd:/code/python/web_test/data.db'
data = pd.read_csv(file)

conn = sqlite3.connect(db_path)
#c = conn.cursor()
conn.execute('drop table if exists gates')
data.to_sql(name = 'gates', con = conn, if_exists = 'replace', index = False)
