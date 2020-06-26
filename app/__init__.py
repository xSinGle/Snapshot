# -*- coding: utf-8 -*-
__author__ = 'SinGle'
__date__ = '2020/06/26 13:01'

from flask import Flask


def create_app():
    app = Flask(__name__)
    register_blueprint(app)
    return app


def register_blueprint(app):
    from app.view import view
    app.register_blueprint(view)
