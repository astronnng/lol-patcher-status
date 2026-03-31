import discord
from discord.ext import tasks, commands
from ..services.riot_data_source import RiotDataSource
from ..services.patch_differ import PatchDiffer
from ..services.classifier import Classifier
from ..services.formatter import Formatter
from ..database.connection import AsyncSessionLocal
from ..database.repository import Repository
from ..models.patch_record import PatchRecord as PatchRecordModel
from ..config import Config
from ..utils.logger import root_logger
from datetime import datetime
import asyncio
import json

class PatchWatcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_source = RiotDataSource()
        self.patch_differ = PatchDiffer(self.data_source)
        self.check_for_patches.start()

    def cog_unload(self):
        self.check_for_patches.cancel()
        asyncio.create_task(self.data_source.close())

    @tasks.loop(minutes=Config.POLLING_INTERVAL)
    async def check_for_patches(self):
        root_logger.info("Verificando atualizações de patch do LoL...")
        try:
            latest_version = await self.data_source.fetch_latest_version()
            if not latest_version: return

            async with AsyncSessionLocal() as session:
                repo = Repository(session)
                last_checked = await repo.get_bot_state("last_checked_version")

                if last_checked == latest_version:
                    root_logger.debug(f"Versão {latest_version} já é a atual. Pulando.")
                    return

                # Nova versão detectada!
                root_logger.info(f"Nova patch detectada: {latest_version}! Iniciando processamento...")
                
                # Fetch versions list to find the previous one
                versions = await self.data_source.get_latest_versions()
                prev_version = versions[1] if len(versions) > 1 else None
                
                # Gerar diferenças
                # PatchDiffer.diff_patches returns List[ChampionChange]
                # Each ChampionChange has classification and StatChanges
                changes = await self.patch_differ.diff_patches(prev_version, latest_version)
                
                # Separar por categorias
                buffs = [c for c in changes if c.classification == "buffed"]
                nerfs = [c for c in changes if c.classification == "nerfed"]
                adjusts = [c for c in changes if c.classification == "adjusted"]
                
                # Criar objeto de domínio PatchRecord
                # Convert back to dict for storage as JSON in ORM
                patch_record = PatchRecordModel(
                    version=latest_version,
                    detected_at=datetime.utcnow(),
                    published_at=None, # Not provided by Data Dragon
                    buffs=buffs,
                    nerfs=nerfs,
                    adjustments=adjusts,
                    raw_data={}
                )
                
                # Guardar no banco
                # Convert dataclasses to dicts for JSON columns
                await repo.add_patch_record(
                    version=latest_version,
                    buffs=[vars(b) for b in buffs],
                    nerfs=[vars(n) for n in nerfs],
                    adjusts=[vars(a) for a in adjusts]
                )
                
                # Notificar Guilds
                active_configs = await repo.get_active_guild_configs()
                for config in active_configs:
                    channel = self.bot.get_channel(config.channel_id)
                    if not channel:
                        # Se não encontrar no cache, tentar buscar (raro, mas possível p/ bots em muitos servers)
                        try:
                            channel = await self.bot.fetch_channel(config.channel_id)
                        except (discord.NotFound, discord.Forbidden):
                            root_logger.warning(f"Canal {config.channel_id} deletado ou inacessível. Desativando config.")
                            await repo.unsubscribe_guild(config.guild_id)
                            continue

                    if channel:
                        try:
                            # 1. Ping role if configured
                            content = ""
                            if config.ping_role_id:
                                role = channel.guild.get_role(config.ping_role_id)
                                content = role.mention if role else ""
                            
                            # 2. Build and send embeds
                            # Formatter handles show_details based on config
                            guild_conf_dict = {"show_details": config.show_details == 1}
                            embeds = Formatter.create_patch_embeds(patch_record, guild_conf_dict)
                            
                            # Send in batches of 10
                            for i in range(0, len(embeds), 10):
                                await channel.send(content=content if i == 0 else "", embeds=embeds[i:i+10])
                            
                        except Exception as e:
                            root_logger.error(f"Falha ao enviar notificação para guild {config.guild_id}: {e}")

                # Atualizar estado do bot
                await repo.set_bot_state("last_checked_version", latest_version)
                await repo.set_bot_state("last_check_timestamp", datetime.utcnow().isoformat())
                root_logger.info(f"Processamento da versão {latest_version} finalizado com sucesso.")

        except Exception as e:
            root_logger.error(f"Erro no loop de verificação de patch: {e}", exc_info=True)

    @check_for_patches.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @check_for_patches.error
    async def check_error(self, ctx, error):
        root_logger.error(f"Erro crítico no loop check_for_patches: {error}")
        # Notificar owner se possível
        owner_id = int(os.getenv("BOT_OWNER_ID", "0"))
        if owner_id:
            owner = self.bot.get_user(owner_id)
            if owner:
                await owner.send(f"🚨 **Erro Crítico no LoL Patch Watcher**: {error}")

async def setup(bot):
    await bot.add_cog(PatchWatcher(bot))
