from typing import List, Literal
from ..models.stat_change import StatChange
from ..utils.logger import root_logger

class Classifier:
    # Stats where INCREASE = BUFF
    BUFF_IF_INCREASED = [
        "damage", "effect", "range", "hp", "armor", "mr", "spellblock", "hp_regen", "hpregen",
        "mpregen", "mp_regen", "attack_speed", "attackspeed", "cc_duration", 
        "shield_duration", "healing", "base_ad", "attackdamage", "movespeed"
    ]
    
    # Stats where DECREASE = BUFF (Cooldowns, Costs)
    BUFF_IF_DECREASED = ["cooldown", "mana_cost", "cost"]

    @classmethod
    def classify_stat_change(cls, stat_name: str, old_value: str, new_value: str) -> str:
        """
        Classifies a single stat change as 'buff' or 'nerf'.
        Handles scaling values like '80/115/150/185/220'.
        """
        stat_name_lower = stat_name.lower().replace(" ", "_")
        
        # Split values to handle scaling (e.g. 80/115/150/185/220)
        old_parts = [float(x.strip()) for x in old_value.replace('/', ' ').split() if cls._is_float(x.strip())]
        new_parts = [float(x.strip()) for x in new_value.replace('/', ' ').split() if cls._is_float(x.strip())]
        
        if not old_parts or not new_parts:
            # Fallback if parsing fails
            return "buff" if len(new_value) > len(old_value) else "nerf"

        buff_count = 0
        nerf_count = 0
        
        # Compare element by element
        for i in range(min(len(old_parts), len(new_parts))):
            v_old = old_parts[i]
            v_new = new_parts[i]
            
            if abs(v_old - v_new) < 0.0001:
                continue
                
            is_increase = v_new > v_old
            
            # Determine if increase is good or bad
            if any(s in stat_name_lower for s in cls.BUFF_IF_INCREASED):
                if is_increase: buff_count += 1
                else: nerf_count += 1
            elif any(s in stat_name_lower for s in cls.BUFF_IF_DECREASED):
                if not is_increase: buff_count += 1
                else: nerf_count += 1
            else:
                # Default: increase = buff
                if is_increase: buff_count += 1
                else: nerf_count += 1

        if buff_count > 0 and nerf_count == 0:
            return "buff"
        elif nerf_count > 0 and buff_count == 0:
            return "nerf"
        elif buff_count > nerf_count:
            return "buff"
        elif nerf_count > buff_count:
            return "nerf"
        
        return "buff" # Tie-break

    @staticmethod
    def classify_champion(changes: List[StatChange]) -> str:
        """
        Classifies the overall champion change based on all its stat changes.
        """
        if not changes:
            return "adjusted" # Should not happen if filtered

        buff_changes = sum(1 for c in changes if c.direction == "buff")
        nerf_changes = sum(1 for c in changes if c.direction == "nerf")
        
        total = len(changes)
        
        if buff_changes == total:
            return "buffed"
        if nerf_changes == total:
            return "nerfed"
        
        # Mix of buff/nerf or contains 'adjust' directions
        return "adjusted"

    @staticmethod
    def _is_float(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
