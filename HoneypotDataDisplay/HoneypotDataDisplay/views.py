"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Flask, request, render_template, jsonify, Response, send_from_directory, stream_with_context
from HoneypotDataDisplay import app, helpers, settings
import psycopg2
import json
import os

def getCount():
    result = helpers.query("SELECT count(*) FROM sshattempts;", one = True)
    return result['count']

def getTopCombo():
    topCombo = helpers.query("SELECT username, password FROM sshattempts GROUP BY username, password ORDER BY count(ID) DESC;", one = True)
    return topCombo

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
    allData['history'] = helpers.query("SELECT date_part('epoch', date_trunc('hours', datetime)) * 1000 as t, Count(ID) FROM sshattempts WHERE datetime > (NOW() - '1 days'::INTERVAL) GROUP BY t ORDER BY t DESC;")
    return Response(json.dumps(allData),  mimetype='application/json')


@app.route('/_timeline')
def event_counts():
    result = helpers.query("SELECT TOP 50 IP, datetime FROM sshattempts WHERE datetime > (NOW() - '1 day'::INTERVAL) ORDER BY datetime DESC;")
    return jsonify({'timeline': result})


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

@app.route('/ohmygodthisisabadidea')
def render_giant_page():
    result = helpers.query("SELECT DateTime, IP, username, password FROM sshattempts ORDER BY datetime DESC;")
    return Response(stream_with_context(stream_template(
        'searchable_list.html',
        title='Home Page',
        year=datetime.now().year,
        all_the_events=result,
    )))