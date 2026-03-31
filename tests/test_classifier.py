import pytest
from bot.services.classifier import Classifier
from bot.models.stat_change import StatChange

def test_damage_increase_classified_as_buff():
    res = Classifier.classify_stat_change("attackdamage", "50", "60")
    assert res == "buff"

def test_damage_decrease_classified_as_nerf():
    res = Classifier.classify_stat_change("attackdamage", "70", "60")
    assert res == "nerf"

def test_cooldown_decrease_classified_as_buff():
    res = Classifier.classify_stat_change("cooldown", "10", "8")
    assert res == "buff"

def test_cooldown_increase_classified_as_nerf():
    res = Classifier.classify_stat_change("cooldown", "8", "10")
    assert res == "nerf"

def test_mana_cost_decrease_classified_as_buff():
    res = Classifier.classify_stat_change("mana cost", "100", "80")
    assert res == "buff"

def test_multi_level_values_buff():
    res = Classifier.classify_stat_change("damage", "80/100/120", "90/110/130")
    assert res == "buff"

def test_mixed_changes_classified_as_adjusted():
    changes = [
        StatChange("Q", "damage", "50", "60", "buff"),
        StatChange("W", "cooldown", "8", "10", "nerf")
    ]
    res = Classifier.classify_champion(changes)
    assert res == "adjusted"

def test_all_buffs_champion_classified_buffed():
    changes = [StatChange("Q", "damage", "50", "60", "buff")]
    res = Classifier.classify_champion(changes)
    assert res == "buffed"

def test_all_nerfs_champion_classified_nerfed():
    changes = [StatChange("Q", "damage", "60", "50", "nerf")]
    res = Classifier.classify_champion(changes)
    assert res == "nerfed"
