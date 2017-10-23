#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A simple flask based API for http://infolanka.com/news/ (by chehanr)."""

from flasgger import Swagger
from flask import Flask, render_template
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from api.v1.routes import API as api_v1

COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml',
                      'application/json', 'application/javascript']
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500
TEMPLATE = {
    'swagger': '2.0',
    'info': {
        'title': 'newsreadr-api',
        'description': 'A simple flask based API for http://infolanka.com/news/',
        'contact': {
            'name': 'chehanr',
            'url': 'https://chehanr.github.io',
        },
        'version': '0.0.1'
    },
    "basePath": "/",
    'schemes': [
        'http',
        'https'
    ]
}

APP = Flask(__name__)
APP.register_blueprint(api_v1, url_prefix='/api/v1')
# TODO make changes to rate limit.
LIMITER = Limiter(APP, key_func=get_remote_address,
                  default_limits=['10 per second', '10000 per day'])
APP.config['SWAGGER'] = {
    'title': 'API Documentation',
    'uiversion': 2
}
SWAG = Swagger(APP, template=TEMPLATE)
Compress(APP)


@APP.route('/')
def root():
    """Show index page."""
    return render_template('index.html')


@APP.route('/api/')
def api_root():
    """Show api information."""
    return render_template('api.html')


if __name__ == '__main__':
    APP.run(debug=False, use_reloader=True)
