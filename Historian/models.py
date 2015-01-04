"""
Define pewee ORM models
"""
import datetime

from peewee import *
from app import database


class BaseModel(Model):
    """
    Base model setting up the database models will use.
    """
    class Meta:
        database = database


class Point(BaseModel):
    """
    A data point - name of the values source.
    """
    point = PrimaryKeyField()
    name = CharField(unique=True)
    filter_type = IntegerField(default=0)
    filter_value = FloatField(default=0)
    limit_hours = IntegerField(default=0)
    units = CharField()

    def __str__(self):
        return "%s" % (self.name,)


class PointValue(BaseModel):
    """
    Timestamped values associated with a point.
    """
    # point = ForeignKeyField(Point, related_name='values')
    value = FloatField()
    timestamp = DateTimeField(default=datetime.datetime.now, primary_key=True)

    def __str__(self):
        return "%s - %s :: %.2f" % (self.point, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.value)

    class Meta:
        # primary_key = CompositeKey('point', 'timestamp')
        order_by = ('timestamp',)


def point_model_factory(name):
    new_class = type(str(name), (PointValue,), {})
    new_class._meta.db_table = name
    return new_class


def get_point_value_models():
    Point.create_table(fail_silently=True)
    point_models = {}
    query = Point.select()
    for point in query:
        point_models[point.name] = create_point_model(point.name)
    return point_models


def get_point_value_model(point_name, create=False):
    point_models = get_point_value_models()
    if point_name in point_models:
        return point_models[point_name]
    elif create:
        return add_point(point_name)
    else:
        return None


def create_point_model(point_name):
    point_model = point_model_factory(point_name)
    point_model.create_table(fail_silently=True)
    return point_model


def add_point(point_name):
        # new entry into the point table
        point = Point()
        point.name = point_name
        point.save(force_insert=True)
        # new model for point values
        return create_point_model(point_name)