# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, request, render_template, send_from_directory
import json
from datetime import datetime
import sqlite3


from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, Row
import json

app = Flask(__name__)
app.static_folder = 'static'

db_path='data.db'

def GetSC():
	conf = SparkConf()
	conf.setAppName('highway').setMaster('local[*]')
	sc = SparkContext(conf = conf)
	spark = SparkSession(sc)
	return sc, spark

def QueryData(gate):
	sc, spark = GetSC()
	data = sc.textFile('d:/code/python/web_test/TDCS_M06A_20180607_180000.csv')
	org_data = data.map(lambda x : x.split(',')).filter(lambda x : x[2] == gate).map(lambda x : Row(car=x[0], start_gate = x[2], price = x[5])).toDF().registerTempTable('traffic')

	query = 'select car, start_gate, count(*) as count, avg(price) as avg_price from traffic where start_gate = "{}" group by car, start_gate'.format(gate)
	result = spark.sql(query).rdd.map(lambda row: row[0]+','+str(row[2])+','+str(row[3])).collect()

	dict_result = []
	for r in result:
		dict_result.append({
		'car':r.split(',')[0],
		'count':r.split(',')[1],
		'price':r.split(',')[2]
		})
	sc.stop()
	return dict_result

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
	
@app.route('/query_gate', methods=['POST'])
def Query():
	gate = request.form.get('gate')
	print('Query gate: {}'.format(gate))
	result = QueryData(gate)
	return render_template('gate.html',gate=gate,results=result)

@app.route('/download')
def download():
	year=['2017','2018']
	month=['01','02','03','04']
	return render_template('download.html')
	
@app.route('/download_file', methods=['POST'])
def download_file():
	abs_path = 'd:/code/python/web_test/'
	year = request.form.get('year')
	month = request.form.get('month')
	print('{}-{}'.format(year, month))
	return '{}-{}'.format(year, month)
	#return send_from_directory(abs_path,'TDCS_M06A_20180607_180000.csv')

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