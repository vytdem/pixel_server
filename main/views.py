import io
import json

from PIL import Image
from django.http import HttpResponse
from django.views.generic import TemplateView
from django_redis import get_redis_connection
from sesame.utils import get_token

from websocket_server import settings


class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_token'] = get_token(self.request.user)
        return context


class InitImageView(TemplateView):
    def get(self, request, *args, **kwargs):
        connection = get_redis_connection()
        pipeline = connection.pipeline()

        it = 0
        for x in range(0, settings.IMAGE_SIZE):
            for y in range(0, settings.IMAGE_SIZE):
                bitfield = pipeline.bitfield('pixel')
                bitfield = bitfield.get('u9', '#' + str(it))
                bitfield = bitfield.get('u9', '#' + str(it + 1))
                bitfield = bitfield.get('u9', '#' + str(it + 2))
                bitfield.execute()
                it += 3

        pixels = pipeline.execute()

        img = Image.new('RGB', (settings.IMAGE_SIZE, settings.IMAGE_SIZE), color=(255,255,255))
        img_data = img.load()

        it = 0
        for x in range(0, settings.IMAGE_SIZE):
            for y in range(0, settings.IMAGE_SIZE):
                img_data[x, y] = (pixels[it][0], pixels[it][1], pixels[it][2])
                it += 1

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')

        return HttpResponse(buffer.getvalue(), content_type='image/png')