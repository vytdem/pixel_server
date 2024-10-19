import uuid as uuid
from cassandra.cqlengine import columns
# from django_cassandra_engine.models import DjangoCassandraModel
from cassandra.cqlengine.models import Model

class ImageOriginal(Model):
    __table_name__ = 'image_original'
    x = columns.Integer(primary_key=True)
    y = columns.Integer(primary_key=True)
    r = columns.Integer()
    g = columns.Integer()
    b = columns.Integer()

class ImageHidden(Model):
    __table_name__ = 'image_hidden'
    x = columns.Integer(primary_key=True)
    y = columns.Integer(primary_key=True)
    r = columns.Integer()
    g = columns.Integer()
    b = columns.Integer()


class ImageOpened(Model):
    __table_name__ = 'image_opened'
    x = columns.Integer(primary_key=True)
    y = columns.Integer(primary_key=True)