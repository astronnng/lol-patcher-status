import discord
from discord.ext import commands
import asyncio
import os
import sys
from .config import Config
from .database.connection import init_db
from .utils.logger import root_logger

# Define intents
intents = discord.Intents.default()
intents.message_content = True # Required for some interactions if needed

class LoLPatchWatcherBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!", # Prefix for standard commands (if any)
            intents=intents,
            help_command=None # Usually custom-built
        )
        self.initial_extensions = [
            'bot.cogs.commands',
            'bot.cogs.patch_watcher'
        ]

    async def setup_hook(self):
        root_logger.info("Initializing database...")
        await init_db()
        
        root_logger.info("Loading extensions...")
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                root_logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                root_logger.error(f"Failed to load extension {extension}: {e}")
        
        # Syncing slash commands
        root_logger.info("Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            root_logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            root_logger.error(f"Failed to sync slash commands: {e}")

    async def on_ready(self):
        root_logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name="Monitorando League of Legends 🕵️"))

async def main():
    try:
        Config.validate()
        bot = LoLPatchWatcherBot()
        async with bot:
            await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        root_logger.info("Shutting down bot...")
    except ValueError as e:
        root_logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        root_logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
