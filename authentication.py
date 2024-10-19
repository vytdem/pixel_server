#!/usr/bin/env python

import asyncio
import json
import os
import random

import aioredis
import django
import websockets
from django_redis import get_redis_connection

from data_handler.models import ImageOpened, ImageOriginal, ImageHidden

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websocket_server.settings")
django.setup()

from django.contrib.contenttypes.models import ContentType
from sesame.utils import get_user

from cassandra.cqlengine import connection
from websocket_server import settings


CONNECTIONS = {}
PIXEL_STATUS = {} # not used pixels dict

redis_connection = get_redis_connection("default")
pipeline = redis_connection.pipeline()

it = 0
for x in range(0, settings.IMAGE_SIZE):
    for y in range(0, settings.IMAGE_SIZE):
        bitfield = pipeline.bitfield('pixelStatus')
        bitfield = bitfield.get('u1', '#' + str(it))
        bitfield.execute()
        it += 1

pixels = pipeline.execute()

it = 0
for x in range(0, settings.IMAGE_SIZE):
    for y in range(0, settings.IMAGE_SIZE):
        if pixels[it][0] == 0:
            PIXEL_STATUS[x, y] = pixels[it][0]
        it += 1

del redis_connection


def save_pixel_data(redis_connection, data):
    ImageHidden.objects(x=data["x"], y=data["y"]).update(r=data["r"], g=data["g"], b=data["b"])
    ImageOpened.create(x=data["x"], y=data["y"])

    iteration = (((settings.IMAGE_SIZE - 1) * 3 + 3) * data["x"]) + (data["y"] * 3)

    bitf = redis_connection.bitfield('pixel')
    bitf = bitf.set('u9', '#' + str(iteration), data["r"])
    bitf = bitf.set('u9', '#' + str(iteration + 1), data["g"])
    bitf = bitf.set('u9', '#' + str(iteration + 2), data["b"])
    bitf.execute()

    iteration2 = (settings.IMAGE_SIZE * data["x"]) + data["y"]

    bitf = redis_connection.bitfield('pixelStatus')
    bitf = bitf.set('u1', '#' + str(iteration2), 1)
    bitf.execute()

def pixel_uncover(message):
    not_used_x, not_used_y = random.choice(list(PIXEL_STATUS.keys()))

    connection.setup(['127.0.0.1'], 'pixel')
    image_original = ImageOriginal.objects(x=not_used_x, y=not_used_y).allow_filtering().get()

    pixel_data = {
        "x": not_used_x,
        "y": not_used_y,
        "r": image_original.r,
        "g": image_original.g,
        "b": image_original.b
    }
    data = {
        "content_type_id": 1,
        "channel": "events",
        "data": pixel_data
    }

    redis_connection = get_redis_connection("default")
    redis_connection.publish("events", json.dumps(data))
    del PIXEL_STATUS[not_used_x, not_used_y]

    save_pixel_data(redis_connection, pixel_data)

def get_content_types(user):
    """Return the set of IDs of content types visible by user."""
    # This does only three database queries because Django caches
    # all permissions on the first call to user.has_perm(...).
    return {
        ct.id
        for ct in ContentType.objects.all()
        if user.has_perm(f"{ct.app_label}.view_{ct.model}")
        or user.has_perm(f"{ct.app_label}.change_{ct.model}")
    }


async def handler(websocket):
    """Authenticate user and register connection in CONNECTIONS."""
    sesame = await websocket.recv()
    loop = asyncio.get_running_loop()

    user = await loop.run_in_executor(None, get_user, sesame)
    if user is None:
        await websocket.close(1011, "authentication failed")
        return

    ct_ids = await loop.run_in_executor(None, get_content_types, user)
    CONNECTIONS[websocket] = {"content_type_ids": ct_ids}

    async for message in websocket:
        pixel_uncover(message)

    try:
        await websocket.wait_closed()
    finally:
        del CONNECTIONS[websocket]


async def process_events():
    """Listen to events in Redis and process them."""
    redis = aioredis.from_url("redis://127.0.0.1:6379/1")
    pubsub = redis.pubsub()
    await pubsub.subscribe("events")
    async for message in pubsub.listen():
        print(message)
        if message["type"] != "message":
            continue
        payload = message["data"].decode()
        # Broadcast event to all users who have permissions to see it.
        event = json.loads(payload)
        recipients = (
            websocket
            for websocket, connection_item in CONNECTIONS.items()
            if event["content_type_id"] in connection_item["content_type_ids"]
        )
        websockets.broadcast(recipients, payload)


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await process_events()  # runs forever


if __name__ == "__main__":
    asyncio.run(main())