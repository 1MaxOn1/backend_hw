import asyncio
import json
import aio_pika
import logging
from typing import Any

logger = logging.getLogger(__name__)

class RabbitMQBroker:
    def __init__(self, url: str = "amqp://guest:guest@rabbitmq/"):
        self.url = url
        self.connection = None
        self.channel = None

    async def connect(self, retries=5, delay=2):
        for attempt in range(retries):
            try:
                self.connection = await aio_pika.connect_robust(self.url)
                self.channel = await self.connection.channel()
                await self.channel.declare_queue("item_created", durable=True)
                logger.info(f"Connected to RabbitMQ on attempt {attempt+1}")
                return
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ (attempt {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise

    async def publish(self, routing_key: str, data: dict):
        if not self.channel:
            raise Exception("RabbitMQ channel is not initialized. Call connect() first.")
        message = aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.channel.default_exchange.publish(message, routing_key=routing_key)
        logger.info(f"Published message to {routing_key}: {data}")

    async def close(self):
        if self.connection:
            await self.connection.close()