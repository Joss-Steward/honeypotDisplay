"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Flask, request, render_template, jsonify, Response
import psycopg2
import json
from HoneypotDataDisplay import app

connection_string = ""

def getCount():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM sshattempts;")
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0]

def getTopCombo():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM sshattempts GROUP BY username, password ORDER BY count(ID) DESC;")
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result

@app.route('/')
@app.route('/home')
def home():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT DateTime, IP, username, password  FROM sshattempts ORDER BY DateTime DESC LIMIT 50;")
    r = [dict((cursor.description[i][0], value) \
                   for i, value in enumerate(row)) for row in cursor.fetchall()]
    conn.commit()
    conn.close()
    topCount = getCount()
    topCombo = getTopCombo()

    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        page_data=r,
        count=topCount,
        topUser=topCombo[0],
        topPassword=topCombo[1],
    )

@app.route('/_password_summary')
def password_summary():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT password as label, COUNT(ID) as data FROM sshattempts GROUP BY password ORDER BY COUNT(ID) DESC LIMIT 10;")
    r = [dict((cursor.description[i][0], value) \
                   for i, value in enumerate(row)) for row in cursor.fetchall()]
    conn.commit()
    conn.close()
    return Response(json.dumps({'passwords': r}),  mimetype='application/json')

@app.route('/_ip_summary')
def ip_summary():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT IP as label, COUNT(ID) as data FROM sshattempts GROUP BY IP ORDER BY COUNT(ID) DESC LIMIT 10;")
    r = [dict((cursor.description[i][0], value) \
                   for i, value in enumerate(row)) for row in cursor.fetchall()]
    conn.commit()
    conn.close()
    return Response(json.dumps({'sources': r}),  mimetype='application/json')

@app.route('/_username_summary')
def username_summary():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT username as label, COUNT(ID) as data FROM sshattempts GROUP BY username ORDER BY COUNT(ID) DESC LIMIT 10;")
    r = [dict((cursor.description[i][0], value) \
                   for i, value in enumerate(row)) for row in cursor.fetchall()]
    conn.commit()
    conn.close()
    return Response(json.dumps({'usernames': r}),  mimetype='application/json')


@app.route('/_timeline')
def event_counts():
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 50 IP, datetime FROM sshattempts WHERE datetime > NOW() ORDER BY datetime DESC;")
    records = cursor.fetchall()
    return jsonify({'source_summary': records})

