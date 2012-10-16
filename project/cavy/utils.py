# -*- coding: utf-8 -*-


import settings


def register_blueprints(app):
    blueprints = getattr(settings, 'ENABLED_BLUEPRINTS', [])

    for bluebrint in blueprints:
        blueprint_object = __import__(bluebrint)
        app.register_blueprint(blueprint_object)
