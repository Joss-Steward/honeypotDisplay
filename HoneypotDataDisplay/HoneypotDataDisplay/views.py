"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Flask, request, render_template, jsonify, Response
from HoneypotDataDisplay import app, helpers, settings
import psycopg2
import json

def getCount():
    result = helpers.query("SELECT count(*) FROM sshattempts;", one = True)
    print(result)
    return result['count']

def getTopCombo():
    topCombo = helpers.query("SELECT username, password FROM sshattempts GROUP BY username, password ORDER BY count(ID) DESC;", one = True)
    print(topCombo)
    return topCombo

@app.route('/')
@app.route('/home')
def home():
    lastFifty = helpers.query("SELECT DateTime, IP, username, password  FROM sshattempts ORDER BY DateTime DESC LIMIT 50;")

    topCount = getCount()
    topCombo = getTopCombo()

    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        page_data=lastFifty,
        count=topCount,
        topUser=topCombo['username'],
        topPassword=topCombo['password'],
    )

@app.route('/_home')
def _home():
    allData = {}
    allData['passwords'] = helpers.query("SELECT password as label, COUNT(ID) as data FROM sshattempts GROUP BY password ORDER BY COUNT(ID) DESC LIMIT 10;")
    allData['usernames'] = helpers.query("SELECT username as label, COUNT(ID) as data FROM sshattempts GROUP BY username ORDER BY COUNT(ID) DESC LIMIT 10;")
    allData['sources'] = helpers.query("SELECT IP as label, COUNT(ID) as data FROM sshattempts GROUP BY IP ORDER BY COUNT(ID) DESC LIMIT 10;")
    return Response(json.dumps(allData),  mimetype='application/json')

@app.route('/_password_summary')
def password_summary():
    result = helpers.query("SELECT password as label, COUNT(ID) as data FROM sshattempts GROUP BY password ORDER BY COUNT(ID) DESC LIMIT 10;")
    return Response(json.dumps({'passwords': result}),  mimetype='application/json')

@app.route('/_ip_summary')
def ip_summary():
    result = helpers.query("SELECT IP as label, COUNT(ID) as data FROM sshattempts GROUP BY IP ORDER BY COUNT(ID) DESC LIMIT 10;")
    return Response(json.dumps({'sources': result}),  mimetype='application/json')

@app.route('/_username_summary')
def username_summary():
    result = helpers.query("SELECT username as label, COUNT(ID) as data FROM sshattempts GROUP BY username ORDER BY COUNT(ID) DESC LIMIT 10;")
    return Response(json.dumps({'usernames': result}),  mimetype='application/json')


@app.route('/_timeline')
def event_counts():
    result = helpers.query("SELECT TOP 50 IP, datetime FROM sshattempts WHERE datetime > DATE_SUB(NOW(), INTERVAL 1 DAY) ORDER BY datetime DESC;")
    return jsonify({'timeline': result})

