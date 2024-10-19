import os

from PIL import Image
from cassandra.cqlengine import connection
from django_redis import get_redis_connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websocket_server.settings")
import django
django.setup()

from data_handler.models import ImageOriginal, ImageHidden, ImageOpened
from websocket_server import settings

def main():
    connection.setup(['127.0.0.1'], 'pixel')

    redis_connection = get_redis_connection()
    pipeline = redis_connection.pipeline()

    data = {}
    for pixel in ImageHidden.objects().limit(settings.IMAGE_SIZE * settings.IMAGE_SIZE):
        data[pixel.x, pixel.y] = (pixel.r, pixel.b, pixel.b)

    it = 0
    for x in range(0, settings.IMAGE_SIZE):
        for y in range(0, settings.IMAGE_SIZE):
            pixel_data = data[x, y]
            bitfield = pipeline.bitfield('pixel')
            bitfield = bitfield.set('u9', '#' + str(it), pixel_data[0])
            bitfield = bitfield.set('u9', '#' + str(it + 1), pixel_data[1])
            bitfield = bitfield.set('u9', '#' + str(it + 2), pixel_data[2])
            bitfield.execute()
            it += 3
    pipeline.execute()

    data_status = {}
    for pixel in ImageOpened.objects().limit(settings.IMAGE_SIZE * settings.IMAGE_SIZE):
        data_status[pixel.x, pixel.y] = 1

    it = 0
    for x in range(0, settings.IMAGE_SIZE):
        for y in range(0, settings.IMAGE_SIZE):
            status = 0
            if (x, y) in data_status:
                status = 1
            bitfield = pipeline.bitfield('pixelStatus')
            bitfield = bitfield.set('u1', '#' + str(it), status)
            bitfield.execute()
            it += 1

    pipeline.execute()
    print('Read from Cassandra database to Redis completed. Total indexes: ', it)


if __name__ == "__main__":
    main()