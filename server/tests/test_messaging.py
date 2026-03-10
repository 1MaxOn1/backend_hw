import pytest
from unittest.mock import AsyncMock, patch
from app.messaging import RabbitMQBroker

@pytest.mark.asyncio
async def test_connect_success():
    broker = RabbitMQBroker()
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = AsyncMock()
        await broker.connect(retries=1, delay=0)
        mock_connect.assert_awaited_once()
        assert broker.connection is not None
        assert broker.channel is not None

@pytest.mark.asyncio
async def test_connect_retries():
    broker = RabbitMQBroker()
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = [Exception("fail"), AsyncMock()]
        await broker.connect(retries=2, delay=0)
        assert mock_connect.call_count == 2

@pytest.mark.asyncio
async def test_connect_all_retries_fail():
    broker = RabbitMQBroker()
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = Exception("fail")
        with pytest.raises(Exception):
            await broker.connect(retries=3, delay=0)
        assert mock_connect.call_count == 3

@pytest.mark.asyncio
async def test_publish():
    broker = RabbitMQBroker()
    broker.channel = AsyncMock()
    broker.channel.default_exchange = AsyncMock()
    await broker.publish("test_key", {"foo": "bar"})
    broker.channel.default_exchange.publish.assert_called_once()

@pytest.mark.asyncio
async def test_publish_without_channel():
    broker = RabbitMQBroker()
    with pytest.raises(Exception, match="RabbitMQ channel is not initialized"):
        await broker.publish("test_key", {"foo": "bar"})

@pytest.mark.asyncio
async def test_close():
    broker = RabbitMQBroker()
    broker.connection = AsyncMock()
    await broker.close()
    broker.connection.close.assert_awaited_once()