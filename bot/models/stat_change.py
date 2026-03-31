from dataclasses import dataclass
from typing import Literal

@dataclass
class StatChange:
    ability: str          # "Passive", "Q", "W", "E", "R", "Base Stats"
    stat_name: str        # "damage", "cooldown", "mana_cost", "base_ad", etc.
    old_value: str        # "80/115/150/185/220"
    new_value: str        # "85/120/155/190/225"
    direction: Literal["buff", "nerf", "adjust"] # "buff" | "nerf" | "adjust"

    def __repr__(self):
        return f"[{self.ability}] {self.stat_name}: {self.old_value} -> {self.new_value} ({self.direction})"
