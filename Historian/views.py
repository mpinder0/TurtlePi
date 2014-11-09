"""
Define web views for flask to handle
"""

from flask import request, render_template

from app import app
from models import Point, PointValue
from utils import *


@app.route('/')
def test_page():
    points = Point.select(Point.name)
    return render_template('index.html', points=points)


@app.route('/point/<string:point_name>', methods=['GET', 'POST'])
def point(point_name):
    p = get_object_or_404(Point, Point.name == point_name)
    message = ""
    if request.method == "POST":
        try:
            p.filter_type = int(request.form['filter_type'])
            p.filter_value = float(request.form['filter_value'])
            p.limit_hours = int(request.form['limit_hours'])
            p.save()
            message = "Submit ok."
        except (TypeError, ValueError):
            message = "Value error."
    point_dict = get_dictionary_from_model(p)
    return render_template('point.html', message=message, **point_dict)


@app.route('/point_values/<string:point_name>', methods=['GET'])
def point_values(point_name):
    return render_template('point_values.html', point_name=point_name)
