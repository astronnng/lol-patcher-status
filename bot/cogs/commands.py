import discord
from discord.ext import commands
from discord import app_commands
from ..database.connection import AsyncSessionLocal
from ..database.repository import Repository
from ..services.formatter import Formatter
from ..models.patch_record import PatchRecord as PatchRecordModel
from ..models.champion_change import ChampionChange
from ..utils.logger import root_logger
import os
import time
from datetime import datetime

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @app_commands.command(name="setup", description="Configura o canal para receber updates de patch do LoL")
    @app_commands.describe(channel="Canal de texto para os patches", role="Cargo para mencionar (opcional)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role = None):
        """
        - Salvar GuildConfig no banco com guild_id, channel_id, ping_role_id
        - Responder com embed de confirmação
        - Enviar mensagem de teste no canal configurado
        """
        async with AsyncSessionLocal() as session:
            repo = Repository(session)
            await repo.update_guild_config(interaction.guild_id, channel.id, role.id if role else None)
        
        embed = discord.Embed(
            title="✅ Configuração Completa!",
            description=f"Canal de patches definido para {channel.mention}.\n" + 
                        (f"Cargo de ping: {role.mention}" if role else "Nenhum cargo de ping configurado."),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Test message in the configured channel
        await channel.send("🚀 **LoL Patch Watcher** ativado neste canal!")

    @app_commands.command(name="unsubscribe", description="Para de enviar updates de patch neste servidor")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def unsubscribe(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            repo = Repository(session)
            await repo.unsubscribe_guild(interaction.guild_id)
        
        await interaction.response.send_message("❌ Inscrição cancelada. Você não receberá mais notificações.", ephemeral=True)

    @app_commands.command(name="lastpatch", description="Mostra o último patch processado")
    @app_commands.describe(version="Versão específica (ex: 14.12)")
    async def lastpatch(self, interaction: discord.Interaction, version: str = None):
        async with AsyncSessionLocal() as session:
            repo = Repository(session)
            record = await repo.get_patch_record(version) if version else await repo.get_latest_patch_record()
            
            if not record:
                await interaction.response.send_message("❌ Nenhuma patch encontrada.", ephemeral=True)
                return
            
            # Map ORM to Dataclass
            # Note: JSON columns return dicts
            patch_data = PatchRecordModel(
                version=record.version,
                detected_at=record.detected_at,
                published_at=record.published_at,
                buffs=[ChampionChange(**c) for c in (record.buffs_json or [])],
                nerfs=[ChampionChange(**c) for c in (record.nerfs_json or [])],
                adjustments=[ChampionChange(**c) for c in (record.adjustments_json or [])],
                raw_data=record.raw_data_json
            )
            
            embeds = Formatter.create_patch_embeds(patch_data)
            await interaction.response.send_message(embeds=embeds[:10])

    @app_commands.command(name="buffs", description="Lista os campeões buffados na patch")
    async def buffs(self, interaction: discord.Interaction, version: str = None):
        async with AsyncSessionLocal() as session:
            repo = Repository(session)
            record = await repo.get_patch_record(version) if version else await repo.get_latest_patch_record()
            
            if not record or not record.buffs_json:
                await interaction.response.send_message("❌ Nenhum buff listado para esta versão.", ephemeral=True)
                return
            
            text = "\n".join([f"🟢 **{c['champion_name']}** — {c['summary']}" for c in record.buffs_json])
            embed = discord.Embed(title=f"⬆️ BUFFS - {record.version}", description=text[:4000], color=discord.Color.green())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="status", description="Mostra status do bot")
    async def status(self, interaction: discord.Interaction):
        async with AsyncSessionLocal() as session:
            repo = Repository(session)
            last_version = await repo.get_bot_state("last_checked_version")
            last_check = await repo.get_bot_state("last_check_timestamp")
            all_configs = await repo.get_active_guild_configs()
            
            uptime = str(datetime.utcnow() - datetime.fromtimestamp(self.start_time)).split('.')[0]
            
            embed = discord.Embed(title="🤖 Status do LoL Patch Watcher", color=discord.Color.blue())
            embed.add_field(name="Versão Atual", value=last_version or "Nenhuma detectada", inline=True)
            embed.add_field(name="Última Verificação", value=last_check or "Nunca", inline=True)
            embed.add_field(name="Servers Ativos", value=str(len(all_configs)), inline=True)
            embed.add_field(name="Uptime", value=uptime, inline=True)
            
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="force-check", description="Força verificação imediata de nova patch (Owner Only)")
    async def force_check(self, interaction: discord.Interaction):
        owner_id = int(os.getenv("BOT_OWNER_ID", "0"))
        if interaction.user.id != owner_id:
            await interaction.response.send_message("🚫 Comando restrito ao desenvolvedor.", ephemeral=True)
            return
        
        watcher = self.bot.get_cog("PatchWatcher")
        if watcher:
            await interaction.response.send_message("🔄 Iniciando verificação forçada...", ephemeral=True)
            await watcher.check_for_patches()
            await interaction.followup.send("✅ Verificação concluída.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Cog PatchWatcher não encontrada.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Commands(bot))
