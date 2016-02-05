"""
The flask application package.
"""

from flask import Flask
from flask_cache import Cache
from flask_assets import Environment, Bundle

import HoneypotDataDisplay.settings
app = Flask(__name__)

# Load all the settings and stuff
settings.init()

app.debug = settings.DebugEnabled
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
assets = Environment(app)

css = Bundle('content/bootstrap.min.css',
            'content/site.css',
            filters='cssmin', output='gen/packed.css')

js = Bundle('scripts/modernizr-2.6.2.js',
            'scripts/jquery-1.10.2.min.js',
            'scripts/d3.3.5.3.min.js',
            'scripts/topojson.min.js',
            'scripts/flot/jquery.flot.js',
            'scripts/flot/jquery.flot.pie.js',
            'scripts/flot/jquery.flot.time.js',
            'scripts/flot/jquery.flot.resize.js',
            'scripts/datamaps.world.min.js',            
            'scripts/bootstrap.min.js',
            'scripts/respond.min.js',
            filters='jsmin', output='gen/packed.js')

assets.register('all_js', js)
assets.register('all_css', css)

import HoneypotDataDisplay.views