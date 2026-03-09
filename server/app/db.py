from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models import Base, Item
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/appdb")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def seed_db():
    async with async_session_maker() as session:
        result = await session.execute(select(Item).limit(1))
        if result.first() is None:
            items = [
                Item(name="Ноутбук", description="Игровой ноутбук", status="created"),
                Item(name="Мышь", description="Беспроводная мышь", status="created"),
                Item(name="Клавиатура", description="Механическая клавиатура", status="created"),
            ]
            session.add_all(items)
            await session.commit()
            print("База данных заполнена тестовыми данными (3 записи).")
        else:
            print("База данных уже содержит записи, пропускаем инициализацию.")