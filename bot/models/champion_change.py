from dataclasses import dataclass
from .stat_change import StatChange
from typing import List

@dataclass
class ChampionChange:
    champion_id: str           # "Ahri"
    champion_name: str         # "Ahri"
    champion_icon_url: str     # URL do ícone via Data Dragon
    classification: str        # "buffed" | "nerfed" | "adjusted"
    stat_changes: List[StatChange]
    summary: str               # Resumo legível: "Q dano ⬆️, W CD ⬇️"

    def __repr__(self):
        return f"<ChampionChange({self.champion_name}, {self.classification}, changes={len(self.stat_changes)})>"
