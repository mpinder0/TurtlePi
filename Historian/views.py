"""
Define web views for flask to handle
"""

from flask import request, render_template

from app import app
from models import *
from utils import *


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


@app.route('/', methods=['GET'])
def point_values():
    return render_template('point_values.html', points=get_point_value_models().keys())
