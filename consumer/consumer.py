import asyncio
import json
import logging
import os
import aio_pika
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from models import Base, Item

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/appdb")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession)

async def connect_rabbitmq_with_retry(retries=5, delay=2):
    for attempt in range(retries):
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            logger.info(f"Connected to RabbitMQ on attempt {attempt+1}")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        item_id = data["id"]
        async with async_session_maker() as session:
            stmt = update(Item).where(Item.id == item_id).values(status="processed")
            await session.execute(stmt)
            await session.commit()
        logger.info(f"Processed item {item_id}")

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    connection = await connect_rabbitmq_with_retry()
    channel = await connection.channel()
    queue = await channel.declare_queue("item_created", durable=True)
    await queue.consume(process_message)
    logger.info("Consumer started, waiting for messages...")
    try:
        await asyncio.Future()  
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())