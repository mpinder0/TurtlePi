"""
Define pewee ORM models
"""
import datetime

from peewee import *
from app import database


class BaseModel(Model):
    class Meta:
        database = database


class Point(BaseModel):
    point_id = PrimaryKeyField()
    name = CharField()

    def __unicode__(self):
        return self.name


class PointValue(BaseModel):
    point_id = ForeignKeyField(Point)
    value = FloatField()
    timestamp = DateTimeField(default=datetime.datetime.now)

    # def __unicode__(self):
    #   return Point.select(Point.name).where(Point.point_id == self.point_id)

    def between(self, start_time, end_time):
        return PointValue.select(Point.name, PointValue.value, PointValue.timestamp).join(Point).where(
            PointValue.timestamp.between(start_time, end_time))

    class Meta:
        primary_key = CompositeKey('point_id', 'timestamp')
        order_by = ('timestamp',)