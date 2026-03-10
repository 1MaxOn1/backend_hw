import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.db import seed_db, init_db

@pytest.mark.asyncio
async def test_seed_db_empty():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.execute.return_value = mock_result
    mock_session.add_all = MagicMock()
    mock_session.commit = AsyncMock()

    with patch("app.db.async_session_maker") as mock_maker:
        mock_maker.return_value.__aenter__.return_value = mock_session
        await seed_db()
        mock_session.execute.assert_called_once()
        mock_session.add_all.assert_called_once()
        mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_seed_db_not_empty():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.first.return_value = MagicMock()
    mock_session.execute.return_value = mock_result
    mock_session.add_all = MagicMock()
    mock_session.commit = AsyncMock()

    with patch("app.db.async_session_maker") as mock_maker:
        mock_maker.return_value.__aenter__.return_value = mock_session
        await seed_db()
        mock_session.execute.assert_called_once()
        mock_session.add_all.assert_not_called()
        mock_session.commit.assert_not_called()