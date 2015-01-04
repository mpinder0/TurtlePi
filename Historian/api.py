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


@app.route('/api/point_values', methods=['GET'])
def get_point_value():
    #point_models = get_point_models()
    #if point_name in point_models:
    #    point_model = point_models[point_name]
    #else:
    #    abort(404)

    query_from = request.args.get("from")
    #query_to = request.args.get("to")
    query_days = request.args.get("days")
    #query_at = request.args.get("at")

    try:
        query_from = DatetimeConverter.to_python(query_from)
        #query_to = DatetimeConverter.to_python(query_to)
        #query_at = DatetimeConverter.to_python(query_at)
    except ValueError:
        abort(400)

    if (query_from is not None) and (query_days is not None):
        query_to = query_from + timedelta(days=int(query_days), microseconds=-1)

    if (query_from is not None) and (query_to is not None):
        # if "from" or "to" timestamps are present in the query string, get values from that time span.
        results = get_values_between(query_from, query_to)
    #elif query_at is not None:
        # if "at" timestamp is present in the query string, get a single value.
    #    results = get_value_at(point_model, query_at)
    else:
        results = get_all_values()

    if not results:
        # no objects found matching the request - 404
        abort(404)

    return app.response_class(json.dumps(results, indent=2), mimetype='application/json')


def get_all_values():
    results = []
    for point_model in get_point_value_models().values():
        query = point_model.select()
        point_results = get_point_values_dict(query)
        results.append(point_results)
    return results


def get_values_between(timestamp_from, timestamp_to):
    results = []
    point_models = get_point_value_models()
    for point_model in point_models.values():
        query = point_model.select()\
            .where(point_model.timestamp.between(timestamp_from, timestamp_to))
        point_results = get_point_values_dict(query)
        results.append(point_results)
    return results


def get_last_value(pv_model):
    query = pv_model.select().order_by(pv_model.timestamp.desc()).limit(1)
    return get_results_from_query(query)


def get_value_at(pv_model, query_at):
    try:
        timestamp_at = DatetimeConverter.to_python(str(query_at))
    except ValueError:
        abort(400)

    span = timedelta(microseconds=999999)
    query = pv_model.select()\
        .where(pv_model.timestamp.between(timestamp_at, timestamp_at + span))\
        .limit(1)

    return get_results_from_query(query)


@app.route('/api/point_value/<string:point_name>/<float:value>', methods=['POST'])
def set_point_value(point_name, value):
    pv_model = get_point_value_model(point_name, create=True)

    enforce_point_limit(point_name)
    new_value = pv_model()
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
        pv_model = get_point_value_model(point_name)
        last_point_value = get_last_value(pv_model)
        if last_point_value is None:
            return True
        else:
            last_value = last_point_value['value']
            value_lower = last_value - point.filter_value
            value_upper = last_value + point.filter_value
            if (value <= value_lower) | (value >= value_upper):
                return True
            else:
                return False
    else:
        return True


def enforce_point_limit(point_name):
    pv_model = get_point_value_model(point_name)
    if pv_model is not None:
        point = Point.get(Point.name == point_name)

        if point.limit_hours > 0:
            limit_hours = timedelta(hours=point.limit_hours)
            cut_off = datetime.now() - limit_hours

            pv_model.delete()\
                .where(pv_model.timestamp < cut_off)\
                .execute()

def get_point_values_dict(query):
    results = get_results_from_query(query)

    datapoints = []
    for point_value in results:
        timestamp = point_value['timestamp']
        datapoint = [
            int(timestamp.strftime("%s"))*1000,
            point_value['value']
        ]
        datapoints.append(datapoint)

    point_dict = {
        'name': query.model_class._meta.db_table,
        'data': datapoints

    }
    return point_dict