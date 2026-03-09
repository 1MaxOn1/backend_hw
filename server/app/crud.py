from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Item
from app.schemas import ItemCreate

async def create_item(db: AsyncSession, item: ItemCreate) -> Item:
    db_item = Item(**item.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_item(db: AsyncSession, item_id: int) -> Item | None:
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()

async def get_items(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item))
    return result.scalars().all()