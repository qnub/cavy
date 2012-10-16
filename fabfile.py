# -*- coding: utf-8 -*-
"""
Cavy management script.

Run as::

    fab build|compile_less|compile_coffee|uglify_js

``build`` make ``compile_less:True``, ``compile_coffee:False`` and ``uglify``.

See API for details.

API -- :mod:`fabfile`
=====================
"""

import os
from fabric.api import *

from fab_settings import *
from project.cavy import settings as cavy_settings


SCRIPT_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(SCRIPT_ROOT, 'project')

ENABLED_BLUEPRINTS = getattr(cavy_settings, 'ENABLED_BLUEPRINTS', None)


def _compile_less(lessc, less_dir, less_opts=''):
    """
    Less compilation.
    """

    if not os.path.exists(less_dir) or not os.path.isdir(less_dir):
        return

    files = os.listdir(less_dir)

    for less_file in files:
        less_file_path = os.path.join(less_dir, less_file)
        if os.path.isfile(less_file_path) and (less_file == 'style.less' or
                                            less_file.endswith('-style.less')):
            css_dir = os.path.join(os.path.dirname(less_dir), 'css')

            if not os.path.exists(css_dir):
                os.makedirs(css_dir)

            if not os.path.isdir(css_dir):
                raise ValueError(
                    'Target CSS dir "{0}" is not directory'.format(
                        css_dir
                    ))

            less_file_name = os.path.splitext(less_file)

            local('{0} {1} {2} {3}'.format(
                    lessc,
                    less_opts,
                    less_file_path,
                    os.path.join(css_dir, less_file_name[0] + '.css')
                ))


def compile_less(indy=True):
    """
    Compile CSS styles from ``.less`` files.

    .. note:: need ``node.js`` for work.

    ``.less`` files placed in ``project/cavy/static/less`` and named
    ``style.less`` or ``*-style.less``. It'll be compiled in
    ``project/cavy/static/css/(style.css|*-style.css)`` and
    you can import your styles there from blueprint's ``static/less``.
    Folders from ``ENABLED_BLUEPRINTS`` is registered in ``lessc`` as paths for
    import.

    :param indy: Also you can make independent styles in your
        blueprints. If compiler find ``style.less`` or ``*-style.less`` files
        in blueprint's ``static/less`` folder it compile independent style
        file in blueprint's
        ``static/css/(style.css|*-style.css)`` and you can separate include it
        into HTML. Other blueprint's ``static/less`` folders isn't registered in
        ``lessc`` as paths for import in this case.

    """

    lessc = os.path.join(SCRIPT_ROOT, 'node_modules', 'less', 'bin',
        'lessc')
    less_dirs = [
        os.path.join(PROJECT_ROOT, 'cavy', 'static', 'less')
    ]

    if ENABLED_BLUEPRINTS:
        for blueprint in ENABLED_BLUEPRINTS:
            app = blueprint.split('.')[0]
            less_dirs.append(os.path.join(PROJECT_ROOT, app, 'static',
                'less'))

    less_opts = '-x --include-path="{0}"'.format(':'.join(less_dirs))
    _compile_less(lessc, less_dirs[0], less_opts)

    if indy:
        del(less_dirs[0])

        for less_dir in less_dirs:
            less_opts = '-x --include-path="{0}"'.format(less_dir)
            _compile_less(lessc, less_dir, less_opts)


def _compile_coffee(coffee, coffee_dir, coffee_opts=''):
    """
    Coffee-script compilation.
    """

    if not os.path.exists(coffee_dir) or not os.path.isdir(coffee_dir):
        return

    js_dir = os.path.join(os.path.dirname(coffee_dir), 'js')

    if not os.path.exists(js_dir):
        os.makedirs(js_dir)

    if not os.path.isdir(js_dir):
        raise ValueError(
            'Target JS dir "{0}" is not directory'.format(
                js_dir
            ))

    local('{0} -c -b {1} -o {2} {3}'.format(
            coffee,
            coffee_opts,
            js_dir,
            coffee_dir,
        ))


def compile_coffee(join=False):
    """
    Compile JS scrypts from .coffee files.

    .. note:: need ``node.js`` for work.

    Search ``static/coffee`` dirs in ``cavy`` app and in ENABLED_BLUEPRINTS for
    ``*.coffee`` files and compile it into ``static/js`` dir.

    :param join: if ``True`` - all ``*.coffee`` files joined into single
        ``static/js/blueprint_app_name.js`` file.
    """

    coffee = os.path.join(SCRIPT_ROOT, 'node_modules', 'coffee-script', 'bin',
        'coffee')
    coffee_dirs = {
        'cavy': os.path.join(PROJECT_ROOT, 'cavy', 'static', 'coffee')
    }

    if ENABLED_BLUEPRINTS:
        for blueprint in ENABLED_BLUEPRINTS:
            app = blueprint.split('.')[0]
            coffee_dirs[app] = os.path.join(PROJECT_ROOT, app, 'static',
                'coffee')

    for app in coffee_dirs:
        if join:
            coffee_opts = '-j {0}.js'.format(app)
        else:
            coffee_opts = ''

        _compile_coffee(coffee, coffee_dirs[app], coffee_opts)


def _uglify_js(uglify, js_dir, uglify_opts=''):
    """
    JS files minification.
    """

    if not os.path.exists(js_dir) or not os.path.isdir(js_dir):
        return

    files = os.listdir(js_dir)

    for js_file in files:
        if js_file.endswith('.js') and not js_file.endswith('.min.js'):
            js_file_path = os.path.join(js_dir, js_file)
            min_js_file = os.path.splitext(js_file)
            min_js_file_path = os.path.join(js_dir, '{0}.min.js'.format(
                min_js_file[0]))

            local('{0} {1} -o {2} {3}'.format(
                    uglify,
                    uglify_opts,
                    min_js_file_path,
                    js_file_path,
                ))


def uglify_js():
    """
    Minificate JS files.

    .. note:: need ``node.js`` for work.

    Search ``static/js`` dirs in ``cavy`` app and in ``ENABLED_BLUEPRINTS`` for
    ``*.js`` files and minificate it into ``static/js`` dir with
    ``original_basename.min.js`` names.
    """

    uglify = os.path.join(SCRIPT_ROOT, 'node_modules', 'uglify-js', 'bin',
        'uglifyjs')
    js_dirs = [
        os.path.join(PROJECT_ROOT, 'cavy', 'static', 'js')
    ]

    if ENABLED_BLUEPRINTS:
        for blueprint in ENABLED_BLUEPRINTS:
            app = blueprint.split('.')[0]
            js_dirs.append(os.path.join(PROJECT_ROOT, app, 'static', 'js'))

    for app in js_dirs:
        _uglify_js(uglify, app)


def build(indy_less=True, join_js=False):
    """
    Build less, coffee, make uglify, etc.

    :param indy_less: make individual styles in blueprints;
    :param join_js: join all compiled js in single file fo each blueprint.
    """

    compile_less(indy_less)
    compile_coffee(join_js)
    uglify_js()


def _deploy(with_build=True):
    """
    Deployment project to GAE cloud (for future realization).
    """

    if with_build:
        build()


def runserver(args=[]):
    """
    Run GAE SDK server.
    """

    build()

    if args:
        params = ' '.join(*args)
    else:
        params = ''

    local('{0} {1} {2} {3}'.format(
        PYTHON,
        os.path.join(GAE_PATH, 'dev_appserver.py'),
        params,
        PROJECT_ROOT
    ))
