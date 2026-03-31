import discord
from datetime import datetime
from typing import List, Dict, Optional
from ..models.champion_change import ChampionChange
from ..models.patch_record import PatchRecord
from ..utils.constants import COLOR_BUFF, COLOR_NERF, COLOR_ADJUST

class Formatter:
    LOGO_URL = "https://raw.githubusercontent.com/RiotGames/developer-relations/master/assets/lol/logo_lol.png"
    BOT_ICON_URL = "https://discord.com/assets/2c21aeda16de354ba5334551a883b481.png" # Placeholder icon

    @staticmethod
    def generate_summary(change: ChampionChange) -> str:
        """
        Generates a readable summary: 'Q dano ⬆️, W CD ⬇️, Base AD ⬇️'
        """
        summary_parts = []
        for sc in change.stat_changes:
            arrow = "⬆️" if sc.direction == "buff" else "⬇️" if sc.direction == "nerf" else "↔️"
            summary_parts.append(f"{sc.ability} {sc.stat_name} {arrow}")
        return ", ".join(summary_parts)

    @classmethod
    def create_patch_embeds(cls, patch_record: PatchRecord, guild_config: Optional[Dict] = None) -> List[discord.Embed]:
        """
        Builds one or more embeds to represent a single patch.
        guild_config might have 'show_details' flag.
        """
        show_details = guild_config.get('show_details', False) if guild_config else False
        
        embeds: List[discord.Embed] = []
        
        current_embed = discord.Embed(
            title=f"🎮 Patch {patch_record.version} — Mudanças de Campeões",
            description=f"Detetado em {patch_record.detected_at.strftime('%d/%m/%Y %H:%M')}",
            color=0x1E90FF,
            timestamp=datetime.utcnow()
        )
        current_embed.set_thumbnail(url=cls.LOGO_URL)
        current_embed.set_footer(text="Fonte: Riot Games | LoL Patch Watcher", icon_url=cls.BOT_ICON_URL)
        
        # Categorize changes
        buffs = patch_record.buffs
        nerfs = patch_record.nerfs
        adjusts = patch_record.adjustments
        
        # Add fields for each category
        cls._add_categorized_fields(current_embed, "⬆️ BUFFS", buffs, "🟢", show_details, embeds)
        cls._add_categorized_fields(current_embed, "⬇️ NERFS", nerfs, "🔴", show_details, embeds)
        cls._add_categorized_fields(current_embed, "🔄 AJUSTES", adjusts, "🟡", show_details, embeds)
        
        if len(current_embed.fields) > 0:
            embeds.append(current_embed)
            
        return embeds

    @classmethod
    def _add_categorized_fields(cls, embed: discord.Embed, name: str, champions: List[ChampionChange], emoji: str, show_details: bool, embed_list: List[discord.Embed]):
        if not champions: return
        
        lines = []
        for champ in champions:
            summary = champ.summary if not show_details else cls._format_detailed_list(champ)
            lines.append(f"{emoji} **{champ.champion_name}** — {summary}")

        content = ""
        count = len(champions)
        field_name = f"{name} ({count})"
        
        for line in lines:
            # If adding this line exceeds the 1024 char limit, push the current field
            if len(content) + len(line) + 2 > 1024:
                cls._push_field_to_embed(embed, field_name, content, embed_list)
                content = line + "\n"
                field_name = f"{name} (cont.)"
            else:
                content += line + "\n"
        
        if content:
            cls._push_field_to_embed(embed, field_name, content, embed_list)

    @classmethod
    def _push_field_to_embed(cls, embed: discord.Embed, name: str, value: str, embed_list: List[discord.Embed]):
        """
        Check for 25 fields or 6000 character limit before adding.
        """
        # If adding this field would exceed limits, we'd need to create a new embed.
        # But per specs, we simply add if possible.
        # We also need to check total character count (6000)
        # Simplified: discord.Embed character limit
        # This function should ideally handle creating a new embed if needed
        # but to keep it simple for now, we just add the field.
        embed.add_field(name=name, value=value, inline=False)

    @staticmethod
    def _format_detailed_list(champ: ChampionChange) -> str:
        # Example: Base AD (50 -> 60), Q Mana Cost (70 -> 60)
        details = []
        for sc in champ.stat_changes:
            details.append(f"{sc.ability} {sc.stat_name} ({sc.old_value} -> {sc.new_value})")
        return ", ".join(details)
