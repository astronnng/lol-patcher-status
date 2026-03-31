import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DISCORD_APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")
    BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))
    
    # Riot
    RIOT_API_KEY = os.getenv("RIOT_API_KEY", "")
    DDRAGON_BASE_URL = os.getenv("DDRAGON_BASE_URL", "https://ddragon.leagueoflegends.com")
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")
    DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"
    
    # Scheduler
    POLLING_INTERVAL = int(os.getenv("POLL_INTERVAL_MINUTES", "30"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/bot.log")
    
    @classmethod
    def validate(cls):
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN not found in environment")
        # RIOT_API_KEY is not strictly mandatory for Data Dragon but good practice.
