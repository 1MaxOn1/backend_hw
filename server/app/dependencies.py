from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.db import async_session_maker

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

def get_broker(request: Request):
    return request.app.state.broker