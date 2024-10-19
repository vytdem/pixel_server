from cassandra.cluster import Cluster
from django.http import HttpResponse

from data_handler.models import ImageOriginal


def index(request):
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace('pixel')
    insert = ImageOriginal(x=0, y=0, r=255, g=255, b=255)
    insert.save()
    cluster.shutdown()
    return HttpResponse('HelloWorld')
