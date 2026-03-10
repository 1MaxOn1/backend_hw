import httpx
from httpx import ASGITransport
from unittest.mock import patch, AsyncMock, ANY
from datetime import datetime
from app.main import app
from app import schemas

def test_create_item():
    mock_broker = AsyncMock()
    app.state.broker = mock_broker
    with patch("app.api.routes.crud.create_item", new_callable=AsyncMock) as mock_create_item:
        mock_item = schemas.Item(
            id=1,
            name="test",
            description="desc",
            status="created",
            created_at=datetime.now()
        )
        mock_create_item.return_value = mock_item
        with httpx.Client(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = client.post("/items", json={"name": "test", "description": "desc"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test"
        assert data["status"] == "created"
        mock_create_item.assert_awaited_once()
        mock_broker.publish.assert_called_once_with("item_created", {"id": 1})

def test_get_item_found():
    mock_item = schemas.Item(
        id=1,
        name="test",
        description="desc",
        status="created",
        created_at=datetime.now()
    )
    with patch("app.api.routes.crud.get_item", new_callable=AsyncMock) as mock_get_item:
        mock_get_item.return_value = mock_item
        with httpx.Client(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = client.get("/items/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "test"
        mock_get_item.assert_awaited_once_with(ANY, 1)

def test_get_item_not_found():
    with patch("app.api.routes.crud.get_item", new_callable=AsyncMock) as mock_get_item:
        mock_get_item.return_value = None
        with httpx.Client(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = client.get("/items/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"
        mock_get_item.assert_awaited_once_with(ANY, 999)
