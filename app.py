import os
from flask import Flask,jsonify,Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import flask_whooshalchemyplus as wb  # Modified

app = Flask(__name__)
app.debug = False
app.config['SECRET_KEY'] = '8b1e36fe-5751-4d53-b4bd-e3e008517c50'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///imdb.db"
app.config['WHOOSH_BASE']="/models.py"
app.config['ADMIN_KEY']="cb993ada-d3ae-43ee-aad0-3a2ec50a70b0"

db=SQLAlchemy(app)
from models import Movies
wb.whoosh_index(app,Movies)
from models import User

def register_blueprints(app):
    """
    performs calls registration
    """
    # prevents circular imports
    from ImdbAPI import API
    from auth import auth
    # in case more than one application working with movies exists
    # define url_prefix for each of them, e.g. url_prefix="/imdb"
    app.register_blueprint(API)
    app.register_blueprint(auth)
register_blueprints(app)
app.run(debug=False)
