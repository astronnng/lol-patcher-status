import pytest
from bot.services.patch_differ import PatchDiffer
from bot.models.stat_change import StatChange
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_ds():
    ds = MagicMock()
    ds.fetch_champion_data = AsyncMock()
    ds.fetch_champion_details = AsyncMock()
    ds.scrape_patch_notes = AsyncMock()
    ds.get_champion_icon_url = MagicMock(return_value="http://icon.png")
    return ds

@pytest.fixture
def differ(mock_ds):
    return PatchDiffer(mock_ds)

def test_detect_stat_increase(differ):
    old = {"attackdamage": 66}
    new = {"attackdamage": 69}
    changes = differ._compare_base_stats(old, new)
    assert len(changes) == 1
    assert changes[0].stat_name == "attackdamage"
    assert changes[0].old_value == "66"
    assert changes[0].new_value == "69"
    assert changes[0].direction == "buff"

def test_detect_stat_decrease(differ):
    old = {"hp": 600}
    new = {"hp": 580}
    changes = differ._compare_base_stats(old, new)
    assert len(changes) == 1
    assert changes[0].direction == "nerf"

def test_no_changes_returns_empty(differ):
    old = {"hp": 600}
    new = {"hp": 600}
    changes = differ._compare_base_stats(old, new)
    assert len(changes) == 0

def test_spell_cooldown_change(differ):
    old_s = [{"cooldown": [7, 7, 7, 7, 7], "cost": [70], "range": [900]}]
    new_s = [{"cooldown": [6, 6, 6, 6, 6], "cost": [70], "range": [900]}]
    changes = differ._compare_spells(old_s, new_s)
    assert len(changes) == 1
    assert changes[0].stat_name == "cooldown"
    assert changes[0].direction == "buff"
