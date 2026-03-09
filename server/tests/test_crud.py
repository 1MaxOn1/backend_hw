import pytest
from unittest.mock import AsyncMock, MagicMock
from app.crud import create_item, get_item, get_items
from app.schemas import ItemCreate
from app.models import Item

@pytest.mark.asyncio
async def test_create_item():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    captured_item = None

    def add_side_effect(item):
        nonlocal captured_item
        captured_item = item
        item.id = 1
        item.status = "created"

    mock_db.add.side_effect = add_side_effect
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    item_data = ItemCreate(name="test", description="desc")
    result = await create_item(mock_db, item_data)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()
    assert captured_item.name == "test"
    assert captured_item.description == "desc"
    assert captured_item.status == "created"
    assert result is captured_item

@pytest.mark.asyncio
async def test_create_item_no_description():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    captured_item = None

    def add_side_effect(item):
        nonlocal captured_item
        captured_item = item
        item.id = 1
        item.status = "created"

    mock_db.add.side_effect = add_side_effect
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    item_data = ItemCreate(name="test", description=None)
    result = await create_item(mock_db, item_data)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()
    assert captured_item.name == "test"
    assert captured_item.description is None
    assert captured_item.status == "created"
    assert result is captured_item

@pytest.mark.asyncio
async def test_get_item_found():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Item(id=1, name="test")
    mock_db.execute.return_value = mock_result

    result = await get_item(mock_db, 1)
    assert result is not None
    mock_db.execute.assert_called_once()
    mock_result.scalar_one_or_none.assert_called_once()

@pytest.mark.asyncio
async def test_get_item_not_found():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = await get_item(mock_db, 999)
    assert result is None
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_items():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [Item(id=1), Item(id=2)]
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    items = await get_items(mock_db)
    assert len(items) == 2
    mock_db.execute.assert_called_once()
    mock_result.scalars.assert_called_once()
    mock_scalars.all.assert_called_once()