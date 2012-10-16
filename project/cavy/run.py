# -*- coding: utf-8 -*-
"""
Initialize Cavy app
"""

from flask import Flask
from flaskext.gae_mini_profiler import GAEMiniProfiler
from utils import register_blueprints
import cavy


app = Flask('cavy')
cavy.app = app
register_blueprints(app)
app.config.from_object('cavy.settings')

# Enable profiler (enabled in non-production environ only)
GAEMiniProfiler(app)

# Pull in URL dispatch routes
import urls
