import os

from PIL import Image
from cassandra.cqlengine import connection
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websocket_server.settings")
import django
django.setup()

from websocket_server import settings

from data_handler.models import ImageOriginal, ImageHidden
from websocket_server import settings
import redis
from django_redis import get_redis_connection

# r = redis.StrictRedis(host=settings.)

def load_file_to_redis():
    # load image into redis
    img = Image.open('staticfiles/img/image3.png')
    data = img.load()
    img_size = img.size

    max_x = img_size[0]
    max_y = img_size[1]

    if data is not None:
        connection = get_redis_connection()
        pipeline = connection.pipeline()

        it = 0
        for x in range(0, max_x):
            for y in range(0, max_y):
                pixel_data = data[x,y]
                bitfield = pipeline.bitfield('pixel')
                bitfield = bitfield.set('u9', '#' + str(it), pixel_data[0])
                bitfield = bitfield.set('u9', '#' + str(it + 1), pixel_data[1])
                bitfield = bitfield.set('u9', '#' + str(it + 2), pixel_data[2])
                bitfield.execute()
                it += 3

        val = pipeline.execute()


def load_image_to_database(request):
    connection.setup(['127.0.0.1'], 'pixel')

    path = 'staticfiles/img/image3.png'

    img = Image.open(os.path.join(settings.BASE_DIR, path))
    data = img.load()
    img_size = img.size

    max_x = img_size[0]
    max_y = img_size[1]

    for x in range(0, max_x):
        for y in range(0, max_y):
            pixel_data = data[x,y]

            ImageOriginal.create(x=x, y=y, r=pixel_data[0], g=pixel_data[1], b=pixel_data[2])
            ImageHidden.create(x=x, y=y, r=0, g=0, b=0)

def load_database_to_redis():
    connection.setup(['127.0.0.1'], 'pixel')

    redis_connection = get_redis_connection()
    pipeline = redis_connection.pipeline()

    data = {}
    for pixel in ImageHidden.objects().limit(settings.IMAGE_SIZE * settings.IMAGE_SIZE):
        data[pixel.x,pixel.y] = (pixel.r, pixel.b, pixel.b)

    it = 0
    for x in range(0, settings.IMAGE_SIZE):
        for y in range(0, settings.IMAGE_SIZE):
            pixel_data = data[x,y]
            bitfield = pipeline.bitfield('pixel')
            bitfield = bitfield.set('u9', '#' + str(it), pixel_data[0])
            bitfield = bitfield.set('u9', '#' + str(it + 1), pixel_data[1])
            bitfield = bitfield.set('u9', '#' + str(it + 2), pixel_data[2])
            bitfield.execute()
            it += 3

    print('Read from Cassandra database to Redis completed. Total indexes: ', it)

    pipeline.execute()



if __name__ == "__main__":
    print('Nothing to execute, no function is set in main method.')
    # print('main')
    # main()
    # load_image_to_database('a')
    # load_image_to_redis()