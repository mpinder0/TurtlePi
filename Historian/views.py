"""
Define web views for flask to handle
"""

from flask import render_template

from app import app
from models import Point, PointValue


@app.route('/')
def test_page():
    point_values = PointValue.select().order_by(PointValue.timestamp)
    return render_template('test.html', values = point_values)