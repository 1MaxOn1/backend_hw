from fastapi.testclient import TestClient
from app.main import app

def test_app_startup():
    assert app.title == "Item Service"

def test_routes_exist():
    routes = [route.path for route in app.routes]
    assert "/items" in routes
    assert "/items/{item_id}" in routes