import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from consumer import process_message, connect_rabbitmq_with_retry

@pytest.mark.asyncio
async def test_process_message():
    message = MagicMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__ = AsyncMock()
    mock_cm.__aexit__ = AsyncMock()
    message.process.return_value = mock_cm
    message.body = json.dumps({"id": 1}).encode()

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()

    with patch("consumer.async_session_maker") as mock_maker:
        mock_maker.return_value.__aenter__.return_value = mock_session

        await process_message(message)

        message.process.assert_called_once()
        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_connect_rabbitmq_success():
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        mock_connect.return_value = AsyncMock()
        conn = await connect_rabbitmq_with_retry(retries=1, delay=0)
        assert conn is not None
        mock_connect.assert_awaited_once()

@pytest.mark.asyncio
async def test_connect_rabbitmq_retries():
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = [Exception("fail"), AsyncMock()]
        conn = await connect_rabbitmq_with_retry(retries=2, delay=0)
        assert conn is not None
        assert mock_connect.call_count == 2

@pytest.mark.asyncio
async def test_connect_rabbitmq_all_fail():
    with patch("aio_pika.connect_robust", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = Exception("fail")
        with pytest.raises(Exception):
            await connect_rabbitmq_with_retry(retries=2, delay=0)
        assert mock_connect.call_count == 2