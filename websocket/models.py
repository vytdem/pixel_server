import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from django.db import models

# Create your models here.


# class ImageOriginal(Model):
#     __table_name__ = 'image_original'
#     username = columns.UUID(primary_key=True, default=uuid.uuid4)
#     x = columns.Integer(index=True)
#     y = columns.Integer(index=True)
#     r = columns.Integer()
#     g = columns.Integer()
#     b = columns.Integer()