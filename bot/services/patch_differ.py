from typing import List, Dict, Any, Optional
from ..models.champion_change import ChampionChange
from ..models.stat_change import StatChange
from .riot_data_source import RiotDataSource
from ..utils.logger import root_logger

class PatchDiffer:
    def __init__(self, data_source: RiotDataSource):
        self.data_source = data_source

    BASE_STATS = [
        "hp", "hpperlevel", "mp", "mpperlevel", "movespeed", "armor", "armorperlevel", 
        "spellblock", "spellblockperlevel", "attackrange", "hpregen", "hpregenperlevel", 
        "mpregen", "mpregenperlevel", "crit", "critperlevel", "attackdamage", 
        "attackdamageperlevel", "attackspeedperlevel", "attackspeed"
    ]

    async def diff_patches(self, old_version: str, new_version: str) -> List[ChampionChange]:
        """
        Compare champion data between two versions and return a list of changes.
        """
        root_logger.info(f"Diffing patches: {old_version} vs {new_version}")
        
        # 1. Fetch data
        old_data = await self.data_source.fetch_champion_data(old_version)
        new_data = await self.data_source.fetch_champion_data(new_version)
        
        # 2. Try to fetch scraping data (priority)
        scraped_notes = await self.data_source.scrape_patch_notes(new_version)
        
        results = []
        
        # Intersection of champions in both versions
        common_ids = set(old_data.keys()).intersection(new_data.keys())
        
        for cid in common_ids:
            old_champ = old_data[cid]
            new_champ = new_data[cid]
            
            # Use scraping first if available
            # If scraping is available, we'll map its results to StatChange
            stat_changes = []
            
            # --- Base Stats Comparison ---
            champ_stat_changes = self._compare_base_stats(old_champ['stats'], new_champ['stats'])
            stat_changes.extend(champ_stat_changes)
            
            # --- Ability (Spells) Comparison ---
            # Data Dragon 'spells' list
            old_details = await self.data_source.fetch_champion_details(old_version, cid)
            new_details = await self.data_source.fetch_champion_details(new_version, cid)
            
            if old_details and new_details:
                ability_changes = self._compare_spells(old_details.get('spells', []), new_details.get('spells', []))
                stat_changes.extend(ability_changes)

            # Heuristic for classification
            if not stat_changes:
                continue
                
            buffs = sum(1 for sc in stat_changes if sc.direction == "buff")
            nerfs = sum(1 for sc in stat_changes if sc.direction == "nerf")
            
            classification = "adjusted"
            if buffs > 0 and nerfs == 0:
                classification = "buffed"
            elif nerfs > 0 and buffs == 0:
                classification = "nerfed"
            
            # Construct summary
            # Limit summary to a few key changes
            summary_parts = []
            for sc in stat_changes[:3]:
                arrow = "⬆️" if sc.direction == "buff" else "⬇️" if sc.direction == "nerf" else "↔️"
                summary_parts.append(f"{sc.ability} {sc.stat_name} {arrow}")
            
            summary = ", ".join(summary_parts)
            if len(stat_changes) > 3:
                summary += " ..."

            results.append(ChampionChange(
                champion_id=cid,
                champion_name=new_champ['name'],
                champion_icon_url=self.data_source.get_champion_icon_url(new_version, cid),
                classification=classification,
                stat_changes=stat_changes,
                summary=summary
            ))
            
        return results

    def _compare_base_stats(self, old_stats: Dict, new_stats: Dict) -> List[StatChange]:
        changes = []
        for stat in self.BASE_STATS:
            v_old = old_stats.get(stat, 0)
            v_new = new_stats.get(stat, 0)
            
            if abs(v_old - v_new) > 0.0001:
                diff = v_new - v_old
                # Note: For some stats higher is always better (buff)
                direction = "buff" if diff > 0 else "nerf"
                
                changes.append(StatChange(
                    ability="Base Stats",
                    stat_name=stat,
                    old_value=str(v_old),
                    new_value=str(v_new),
                    direction=direction
                ))
        return changes

    def _compare_spells(self, old_spells: List[Dict], new_spells: List[Dict]) -> List[StatChange]:
        changes = []
        # Q, W, E, R are indices 0-3
        labels = ["Q", "W", "E", "R"]
        
        for i in range(min(len(old_spells), len(new_spells), 4)):
            old_s = old_spells[i]
            new_s = new_spells[i]
            label = labels[i]
            
            # Cooldown (CD) - lower is better (buff)
            old_cd = "/".join(map(str, old_s.get('cooldown', [])))
            new_cd = "/".join(map(str, new_s.get('cooldown', [])))
            if old_cd != new_cd:
                # Naive direction check: check first level
                v_old = old_s['cooldown'][0] if old_s['cooldown'] else 0
                v_new = new_s['cooldown'][0] if new_s['cooldown'] else 0
                direction = "buff" if v_new < v_old else "nerf"
                changes.append(StatChange(label, "cooldown", old_cd, new_cd, direction))
            
            # Cost - lower is better (buff)
            old_cost = "/".join(map(str, old_s.get('cost', [])))
            new_cost = "/".join(map(str, new_s.get('cost', [])))
            if old_cost != new_cost:
                v_old = old_s['cost'][0] if old_s['cost'] else 0
                v_new = new_s['cost'][0] if new_s['cost'] else 0
                direction = "buff" if v_new < v_old else "nerf"
                changes.append(StatChange(label, "mana_cost", old_cost, new_cost, direction))

            # Range - higher is usually better
            old_range = "/".join(map(str, old_s.get('range', [])))
            new_range = "/".join(map(str, new_s.get('range', [])))
            if old_range != new_range:
                v_old = old_s['range'][0] if old_s['range'] else 0
                v_new = new_s['range'][0] if new_s['range'] else 0
                direction = "buff" if v_new > v_old else "nerf"
                changes.append(StatChange(label, "range", old_range, new_range, direction))

        return changes
