"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Flask, request, render_template, jsonify, Response, send_from_directory, stream_with_context
from HoneypotDataDisplay import app, helpers, settings, cache
from geoip import geolite2
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
    lastFifty = helpers.query("SELECT DateTime, IP, username, password FROM sshattempts ORDER BY DateTime DESC LIMIT 50;")

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

# So a chart gets a little out of date... not really a huge deal.
@cache.cached(timeout=600, key_prefix='_home')
@app.route('/_home')
def _home():
    allData = {}
    allData['passwords'] = helpers.query("SELECT password as label, COUNT(ID) as data FROM sshattempts GROUP BY password ORDER BY COUNT(ID) DESC LIMIT 10;")
    allData['usernames'] = helpers.query("SELECT username as label, COUNT(ID) as data FROM sshattempts GROUP BY username ORDER BY COUNT(ID) DESC LIMIT 10;")
    allData['sources'] = helpers.query("SELECT IP as label, COUNT(ID) as data FROM sshattempts GROUP BY IP ORDER BY COUNT(ID) DESC LIMIT 10;")
    allData['history'] = helpers.query("SELECT date_part('epoch', date_trunc('hours', datetime)) * 1000 as t, Count(ID) FROM sshattempts WHERE datetime > (NOW() - '1 days'::INTERVAL) GROUP BY t ORDER BY t DESC;")
    return Response(json.dumps(allData),  mimetype='application/json')

# The map might render a little out of date, but this is a pretty time-consuming function otherwise.
@cache.cached(timeout=1800, key_prefix='map_data')
@app.route('/_map')
def map_data():
    attack_sources = helpers.query("SELECT IP as ip, COUNT(ID) as attempts, MIN(DateTime) as first_attempt, MAX(DateTime) as last_attempt FROM sshattempts GROUP BY IP ORDER BY COUNT(ID) DESC;")
    total_attacks = helpers.query("SELECT count(*) FROM sshattempts;", one = True)
    attack_summaries = []

    for point in attack_sources:
        origin = geolite2.lookup(point['ip'])

        if origin is not None:
            radius = ((point['attempts'] / total_attacks['count']) * 100)
            fill = 'SML'

            if radius > 40:
                fill = 'BIG'
            elif radius > 20:
                fill = 'MED'
            elif radius < 5:
                radius = 5

            attack_summaries.append({
                'IP': point['ip'],
                'latitude': origin.location[0],
                'longitude': origin.location[1],
                'count': point['attempts'],
                'fillKey': fill,
                'firstAttempt': point['first_attempt'].strftime('%Y-%m-%d %H:%M:%S'),
                'lastAttempt': point['last_attempt'].strftime('%Y-%m-%d %H:%M:%S'),
                'radius': radius
            })
    return Response(json.dumps(attack_summaries),  mimetype='application/json')

@app.route('/api.csv')
def you_asked_for_it():
    def csv():
        conn = psycopg2.connect(settings.ConnectionString)
        cursor = conn.cursor()
        query = "SELECT DateTime, IP, username, password FROM sshattempts ORDER BY DateTime DESC;"
        cursor.execute(query)

        yield ','.join(d[0] for d in cursor.description) + '\r\n'
        
        for row in cursor.fetchall():
            yield ','.join(str(e) for e in row) + '\r\n'

    return Response(csv(), mimetype='text/csv')