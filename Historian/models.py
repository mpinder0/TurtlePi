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

    def __str__(self):
        return "%s" % (self.name,)


class PointValue(BaseModel):
    """
    Timestamped values associated with a point.
    """
    point = ForeignKeyField(Point, related_name='values')
    value = FloatField()
    timestamp = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return "%s - %s :: %.2f" % (self.point, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.value)

    class Meta:
        primary_key = CompositeKey('point', 'timestamp')
        order_by = ('-timestamp',)


def create_tables():
    database.connect()
    database.create_tables([Point, PointValue], safe=True)