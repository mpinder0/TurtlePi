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
    point_id = PrimaryKeyField()
    name = CharField(unique=True)

    def __str__(self):
        return "%s" % (self.name,)


class PointValue(BaseModel):
    """
    Timestamped values associated with a point.
    """
    point_id = ForeignKeyField(Point)
    value = FloatField()
    timestamp = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return "%s - %s :: %.2f" % (self.point_id, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.value)
        #return "%s - %s - %s" % (self.point_id, self.value, self.timestamp.isoformat())

    class Meta:
        primary_key = CompositeKey('point_id', 'timestamp')
        order_by = ('timestamp',)


def create_tables():
    database.connect()
    database.create_tables([Point, PointValue])