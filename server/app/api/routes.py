from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.dependencies import get_db, get_broker
from app.messaging import RabbitMQBroker

router = APIRouter()

@router.post("/items", response_model=schemas.Item, status_code=201)
async def create_item(
    item: schemas.ItemCreate,
    db: AsyncSession = Depends(get_db),
    broker: RabbitMQBroker = Depends(get_broker)
):
    db_item = await crud.create_item(db, item)
    await broker.publish("item_created", {"id": db_item.id})
    return db_item

@router.get("/items/{item_id}", response_model=schemas.Item)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.get("/items", response_model=list[schemas.Item])
async def list_items(db: AsyncSession = Depends(get_db)):
    items = await crud.get_items(db)
    return items