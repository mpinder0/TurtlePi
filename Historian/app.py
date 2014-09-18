"""
App is home of the flask instance and database setup
"""
from flask import Flask, g
from peewee import *


app = Flask(__name__)
app.config.from_object(__name__)

DATABASE = 'TurtlePi.db'
database = SqliteDatabase(DATABASE, threadlocals=True)


@app.before_request
def before_request():
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response