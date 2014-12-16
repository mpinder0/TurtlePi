"""
Define REST API routes and methods for flask to handle
"""

from datetime import timedelta

from flask import jsonify
from flask import request

import json

from app import app
from models import *
from utils import *


@app.route('/api/point/<string:point_name>', methods=['GET'])
def get_point(point_name):
    point = get_object_or_404(Point, Point.name == point_name)
    dictionary = get_dictionary_from_model(point)
    return jsonify(dictionary)


@app.route('/api/point/<string:point_name>', methods=['POST'])
def set_point(point_name):
    filter_type = request.args.get("filter_type")
    filter_value = request.args.get("filter_value")
    limit_hours = request.args.get("limit")

    try:
        point = Point.get(Point.name == point_name)
    except DoesNotExist:
        point = Point()
        point.name = point_name

    if filter_type is not None:
        try:
            point.filter_type = int(filter_type)
            point.filter_value = float(filter_value)
        except (TypeError, ValueError):
            abort(400)

    if limit_hours is not None:
        try:
            point.limit_hours = int(limit_hours), 201
        except (TypeError, ValueError):
            abort(400)

    point.save()
    return jsonify(get_dictionary_from_model(point))


@app.route('/api/point_values/<string:point_name>', methods=['GET'])
def get_point_value(point_name):
    point_models = get_point_models()
    if point_name in point_models:
        point_model = point_models[point_name]
    else:
        abort(404)

    query_from = request.args.get("from")
    query_to = request.args.get("to")
    query_at = request.args.get("at")

    if (query_from is not None) | (query_to is not None):
        # if "from" or "to" timestamps are present in the query string, get values from that time span.
        results = get_values_between(point_model, query_from, query_to)
    elif query_at is not None:
        # if "at" timestamp is present in the query string, get a single value.
        results = get_value_at(point_model, query_at)
    else:
        results = get_point_values_dict(point_name)

    if not results:
        # no objects found matching the request - 404
        abort(404)

    return app.response_class(json.dumps(results, indent=2), mimetype='application/json')


def get_all_values(point_model):
    # enforce_point_limit(point_name)
    query = point_model.select()
    return get_charts_dict_from_query(query)


def get_last_value(point_model):
    query = point_model.select().limit(1)
    return get_dictionary_from_query(query)


def get_values_between(point_model, query_from, query_to):
    try:
        timestamp_from = DatetimeConverter.to_python(str(query_from))
        timestamp_to = DatetimeConverter.to_python(str(query_to))
    except ValueError:
        abort(400)

    query = point_model.select()\
        .where(point_model.timestamp.between(timestamp_from, timestamp_to))

    return get_charts_dict_from_query(query)


def get_value_at(point_model, query_at):
    try:
        timestamp_at = DatetimeConverter.to_python(str(query_at))
    except ValueError:
        abort(400)

    span = timedelta(microseconds=999999)
    query = point_model.select()\
        .where(point_model.timestamp.between(timestamp_at, timestamp_at + span))\
        .limit(1)

    return get_dictionary_from_query(query)


@app.route('/api/point_value/<string:point_name>/<float:value>', methods=['POST'])
def set_point_value(point_name, value):
    models = get_point_models()
    if point_name in models:
        point_model = models[point_name]
    else:
        point_model = add_point(point_name)

    enforce_point_limit(point_name)
    new_value = point_model()
    new_value.value = value
    value_dict = get_dictionary_from_model(new_value)

    if value_filter_pass(point_name, value):
        new_value.save(force_insert=True)
        value_dict['filter_passed'] = True
    else:
        value_dict['filter_passed'] = False

    return jsonify(value_dict), 201


def value_filter_pass(point_name, value):
    point = Point.get(Point.name == point_name)
    if point.filter_type == 1:
        # fixed hysteresis
        try:
            last_value = get_point_models()[point_name].get().value
        except DoesNotExist:
            return True

        value_lower = last_value - point.filter_value
        value_upper = last_value + point.filter_value
        if (value <= value_lower) | (value >= value_upper):
            return True
        else:
            return False
    else:
        return True


def enforce_point_limit(point_name):
    try:
        point = Point.get(Point.name == point_name)
    except DoesNotExist:
        abort(500)

    point_model = get_point_models()[point_name]

    if point.limit_hours > 0:
        limit_hours = timedelta(hours=point.limit_hours)
        cut_off = datetime.now() - limit_hours

        point_model.delete()\
            .where(point_model.timestamp < cut_off)\
            .execute()


def get_point_model(point_name):
    point_models = get_point_models()
    if point_name in point_models:
        point_model = point_models[point_name]
    else:
        abort(404)
    return point_model


def get_point_values_dict(point_name):
    point_model = get_point_model(point_name)

    query = point_model.select().order_by(point_model.timestamp)
    results = get_dictionary_from_query(query)

    datapoints = []
    for point_value in results.items():
        timestamp = point_value[1]['timestamp']
        datapoint = [
            int(timestamp.strftime("%s"))*1000,
            point_value[1]['value']
        ]
        datapoints.append(datapoint)

    point_dict = {
        'name': point_name,
        'data': datapoints

    }
    return [point_dict]