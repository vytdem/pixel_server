import os

from PIL import Image
from cassandra.cqlengine import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websocket_server.settings")
import django
django.setup()

from data_handler.models import ImageOriginal, ImageHidden
from websocket_server import settings

def main():
    connection.setup(['127.0.0.1'], 'pixel')

    path = 'staticfiles/img/image3.png'

    img = Image.open(os.path.join(settings.BASE_DIR, path))
    data = img.load()
    img_size = img.size

    max_x = img_size[0]
    max_y = img_size[1]

    for x in range(0, max_x):
        for y in range(0, max_y):
            pixel_data = data[x, y]

            ImageOriginal.create(x=x, y=y, r=pixel_data[0], g=pixel_data[1], b=pixel_data[2])
            ImageHidden.create(x=x, y=y, r=0, g=0, b=0)


if __name__ == "__main__":
    main()