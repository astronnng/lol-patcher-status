import pytest
from bot.services.riot_data_source import RiotDataSource
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp

@pytest.mark.asyncio
async def test_fetch_latest_version_returns_string():
    ds = RiotDataSource()
    with patch.object(ds, '_request_with_retry', new_callable=AsyncMock) as mock_req:
        mock_req.return_value = ["14.12.1", "14.11.1"]
        ver = await ds.fetch_latest_version()
        assert ver == "14.12.1"
        mock_req.assert_called_once()
    await ds.close()

@pytest.mark.asyncio
async def test_fetch_champion_data_returns_dict():
    ds = RiotDataSource()
    with patch.object(ds, '_request_with_retry', new_callable=AsyncMock) as mock_req:
        mock_req.return_value = {"data": {"Ahri": {"id": "Ahri"}}}
        data = await ds.fetch_champion_data("14.12.1")
        assert "Ahri" in data
    await ds.close()

@pytest.mark.asyncio
async def test_cache_hit_avoids_request():
    ds = RiotDataSource()
    ds._cache_versions = ["14.12.1"]
    with patch.object(ds, '_request_with_retry', new_callable=AsyncMock) as mock_req:
        ver = await ds.fetch_latest_version()
        assert ver == "14.12.1"
        mock_req.assert_not_called()
    await ds.close()
