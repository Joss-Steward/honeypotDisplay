"""
The flask application package.
"""

from flask import Flask
import HoneypotDataDisplay.settings
app = Flask(__name__)

# Load all the settings and stuff
settings.init()

app.debug = settings.DebugEnabled

import HoneypotDataDisplay.views