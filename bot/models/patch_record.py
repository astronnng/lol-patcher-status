from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from .champion_change import ChampionChange

@dataclass
class PatchRecord:
    version: str                          # "14.12"
    detected_at: datetime
    published_at: Optional[datetime]
    buffs: List[ChampionChange]
    nerfs: List[ChampionChange]
    adjustments: List[ChampionChange]
    raw_data: Optional[Dict]
    notified_guilds: List[int] = field(default_factory=list)

    def __repr__(self):
        return f"<PatchRecord({self.version}, B:{len(self.buffs)}, N:{len(self.nerfs)}, A:{len(self.adjustments)})>"
