"""
Define REST API routes and methods for flask to handle
"""

from datetime import timedelta

from flask import jsonify
from flask import request

from app import app
from models import Point, PointValue
from utils import *



@app.route('/api/point/<string:point_name>', methods=['GET'])
def get_point(point_name):
    obj = get_object_or_404(Point, Point.name == point_name)
    dictionary = get_dictionary_from_model(obj)
    return jsonify(dictionary)


@app.route('/api/point_value/<string:point_name>', methods=['GET'])
def get_point_value(point_name):
    query_from = request.args.get("from")
    query_to = request.args.get("to")
    query_at = request.args.get("at")

    if (query_from is not None) | (query_to is not None):
        # if "from" or "to" timestamps are present in the query string, get values from that time span.
        results = get_values_between(point_name, query_from, query_to)
    elif query_at is not None:
        # if "at" timestamp is present in the query string, get a single value.
        results = get_value_at(point_name, query_at)
    else:
        results = get_all_values(point_name)

    if not results:
        # no objects found matching the request - 404
        abort(404)
    return jsonify(results)


def get_all_values(point_name):
    query = PointValue.select().join(Point).where(Point.name == point_name)
    return get_dictionary_from_query(query)


def get_values_between(point_name, query_from, query_to):
    try:
        timestamp_from = DatetimeConverter.to_python(str(query_from))
        timestamp_to = DatetimeConverter.to_python(str(query_to))
    except ValueError:
        abort(400)

    query = PointValue.select().join(Point)\
        .where(Point.name == point_name)\
        .where(PointValue.timestamp.between(timestamp_from, timestamp_to))

    return get_dictionary_from_query(query)


def get_value_at(point_name, query_at):
    try:
        timestamp_at = DatetimeConverter.to_python(str(query_at))
    except ValueError:
        abort(400)

    span = timedelta(microseconds=999999)
    query = PointValue.select().join(Point)\
        .where(Point.name == point_name)\
        .where(PointValue.timestamp.between(timestamp_at, timestamp_at + span))\
        .limit(1)

    return get_dictionary_from_query(query)


@app.route('/api/point_value/<string:point_name>/<float:value>', methods=['POST'])
def set_point_value(point_name, value):
    try:
        point = Point.get(Point.name == point_name)
    except DoesNotExist:
        abort(404)
    new_value = PointValue.create(point_id=point, value=value)
    return jsonify(get_dictionary_from_model(new_value))