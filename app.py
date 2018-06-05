# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, request, render_template
import json
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.static_folder = 'static'

db_path='data.db'

def get_db():
	db = sqlite3.connect(db_path)
	return db

def convert_highway(high):
	if high == 'one':
		return '國道一號'
	elif high == 'three':
		return '國道三號'
	elif high == 'five':
		return '國道五號'
	elif high == 'all':
		return 'ALL'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def filter():
	db = get_db()
	highway = convert_highway(request.form.get('highway','ALL'))
	main_sql = 'select 國道別, 起點交流道, 迄點交流道, 收費區位代碼, 方向, 北緯, 東經 from gates '
	result = []
	if highway == 'ALL':
		main_sql += 'order by 國道別, 收費區位代碼, 方向'
		cursor = db.execute(main_sql).fetchall()
		for row in cursor:
			result.append({
			'high_no':row[0],
			'start': row[1],
			'end': row[2],
			'id': row[3],
			'direction': row[4],
			'lat': row[5],
			'lon': row[6]
			})
	else:
		main_sql += "where 國道別 like '{}%' order by 收費區位代碼, 方向".format(highway)
		cursor = db.execute(main_sql).fetchall()
		for row in cursor:
			result.append({
			'high_no':row[0],
			'start': row[1],
			'end': row[2],
			'id': row[3],
			'direction': row[4],
			'lat': row[5],
			'lon': row[6]
			})
	with db:
		db.execute('insert into query_history values (?,?)',(highway, datetime.now(),))
	db.close()
	return render_template('result.html',count=len(result),results=result)
	
@app.route('/history')
def history():
	db = get_db()
	query = 'select highway, time from query_history order by time desc'
	rows = db.execute(query).fetchall()
	result = []
	for row in rows:
		result.append({
		'highway': row[0],
		'time': row[1]
		})
	db.close()
	return render_template('history.html',results=result)

@app.route('/reset')
def reset():
	db = get_db()
	result = []
	with db:
		query = 'select count(time) from query_history'
		before = db.execute(query).fetchall()
		for r in before:
			result.append({'sit':'Before','count':r[0]})
		clear = 'delete from query_history'
		db.execute(clear)
		after = db.execute(query).fetchall()
		for a in after:
			result.append({'sit':'After','count':a[0]})
	return render_template('reset.html',results=result)
	
	
if __name__ == "__main__":
    app.run(port=5000, debug = True)