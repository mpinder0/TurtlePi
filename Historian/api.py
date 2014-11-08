"""
Define REST API routes and methods for flask to handle
"""

from datetime import timedelta

from flask import jsonify
from flask import request

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


@app.route('/api/point_value/<string:point_name>', methods=['GET'])
def get_point_value(point_name):
    if not point_name in point_models:
        abort(404)

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
    # enforce_point_limit(point_name)

    query = point_models[point_name].select()
    return get_charts_dict_from_query(query)


def get_last_value(point_name):
    query = point_models[point_name].select().limit(1)
    return get_dictionary_from_query(query)


def get_values_between(point_name, query_from, query_to):
    try:
        timestamp_from = DatetimeConverter.to_python(str(query_from))
        timestamp_to = DatetimeConverter.to_python(str(query_to))
    except ValueError:
        abort(400)

    model_class = point_models[point_name]
    query = model_class.select()\
        .where(model_class.timestamp.between(timestamp_from, timestamp_to))

    return get_charts_dict_from_query(query)


def get_value_at(point_name, query_at):
    try:
        timestamp_at = DatetimeConverter.to_python(str(query_at))
    except ValueError:
        abort(400)

    span = timedelta(microseconds=999999)
    model_class = point_models[point_name]
    query = model_class.select()\
        .where(model_class.timestamp.between(timestamp_at, timestamp_at + span))\
        .limit(1)

    return get_dictionary_from_query(query)


@app.route('/api/point_value/<string:point_name>/<float:value>', methods=['POST'])
def set_point_value(point_name, value):
    if not point_name in point_models:
        add_point(point_name)

    new_value = point_models[point_name]()
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
            last_value = point_models[point_name].get().value
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
    point = get_object_or_404(Point, Point.name == point_name)
    if point.limit_hours > 0:
        limit_hours = timedelta(hours=point.limit_hours)
        cut_off = datetime.now() - limit_hours

        model_class = point_models[point_name]
        model_class.delete()\
            .where(model_class.timestamp < cut_off)\
            .execute()