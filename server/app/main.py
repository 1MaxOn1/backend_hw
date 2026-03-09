from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.metrics import setup_metrics
from app.messaging import RabbitMQBroker
from app.db import engine, init_db, seed_db   

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_db()
    broker = RabbitMQBroker()
    await broker.connect()
    app.state.broker = broker
    yield
    await broker.close()
    await engine.dispose()

app = FastAPI(title="Item Service", lifespan=lifespan)
app.include_router(router)
setup_metrics(app)