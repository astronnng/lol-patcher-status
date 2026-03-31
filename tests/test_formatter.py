import pytest
from bot.services.formatter import Formatter
from bot.models.champion_change import ChampionChange
from bot.models.stat_change import StatChange
from bot.models.patch_record import PatchRecord
from datetime import datetime

def test_embed_has_correct_title():
    patch = PatchRecord("14.12", datetime.utcnow(), None, [], [], [], {})
    embeds = Formatter.create_patch_embeds(patch)
    assert len(embeds) == 1
    assert "Patch 14.12" in embeds[0].title

def test_embed_buffs_field_present_when_buffs_exist():
    champ = ChampionChange("Ahri", "Ahri", "http://icon", "buffed", [StatChange("Base Stats", "AD", "53", "55", "buff")], "Q buff")
    patch = PatchRecord("14.12", datetime.utcnow(), None, [champ], [], [], {})
    embeds = Formatter.create_patch_embeds(patch)
    assert any("BUFFS" in f.name for f in embeds[0].fields)

def test_embed_nerfs_field_absent_when_no_nerfs():
    patch = PatchRecord("14.12", datetime.utcnow(), None, [], [], [], {})
    embeds = Formatter.create_patch_embeds(patch)
    assert not any("NERFS" in f.name for f in embeds[0].fields)

def test_summary_format_correct():
    champ = ChampionChange("Ahri", "Ahri", "http://icon", "buffed", [StatChange("Q", "Dano", "10", "20", "buff")], "")
    summary = Formatter.generate_summary(champ)
    assert "Q Dano ⬆️" in summary

def test_long_list_splits_into_multiple_fields():
    # Create 50 champions to force field split (limit 1024 chars per field)
    buffs = []
    for i in range(50):
        buffs.append(ChampionChange(f"C{i}", f"Champ {i}", "url", "buffed", [], "Very long summary data to fill the field capacity quickly"))
    
    patch = PatchRecord("14.12", datetime.utcnow(), None, buffs, [], [], {})
    embeds = Formatter.create_patch_embeds(patch)
    
    buff_fields = [f for f in embeds[0].fields if "BUFFS" in f.name]
    assert len(buff_fields) > 1
    assert any("(cont.)" in f.name for f in buff_fields)
