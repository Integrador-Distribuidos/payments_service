import asyncio
import aio_pika
import json
import logging
import os
import aio_pika.abc

AMQP_USER = os.getenv("RABBITMQ_USER")
AMQP_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
AMQP_HOST = os.getenv("RABBITMQ_HOST")
AMQP_PORT = os.getenv("RABBITMQ_PORT")
QUEUE_NAME = "order_queue"
AMQP_URL = f"amqp://{AMQP_USER}:{AMQP_PASSWORD}@{AMQP_HOST}:{AMQP_PORT}/"


async def get_connection() -> aio_pika.abc.AbstractRobustConnection:
    """
    Establishes a connection to the AMQP server.
    :return: An instance of RobustConnection.
    """
    logging.info(f"Connecting to AMQP server at {AMQP_URL}")

    return await aio_pika.connect_robust(AMQP_URL, loop=asyncio.get_event_loop())



async def publish_order(message_data: dict):
    connection = await get_connection()
    channel = await connection.channel()

    message_body = json.dumps(message_data).encode()

    await channel.default_exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key=QUEUE_NAME,
    )
    print(f"Mensagem publicada: {message_data}")

    await connection.close()