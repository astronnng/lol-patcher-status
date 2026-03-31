from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, JSON, func, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class GuildConfigORM(Base):
    __tablename__ = 'guild_configs'
    
    guild_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    ping_role_id = Column(BigInteger, nullable=True)
    language = Column(String(10), server_default='pt-BR')
    show_details = Column(Integer, server_default='1') # 1=True, 0=False
    enabled = Column(Integer, server_default='1')      # 1=True, 0=False
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class PatchRecordORM(Base):
    __tablename__ = 'patch_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), unique=True, nullable=False)
    detected_at = Column(DateTime, nullable=False)
    published_at = Column(DateTime, nullable=True)
    buffs_json = Column(JSON, nullable=True)        # Serialized list[ChampionChange]
    nerfs_json = Column(JSON, nullable=True)        # Serialized list[ChampionChange]
    adjustments_json = Column(JSON, nullable=True)  # Serialized list[ChampionChange]
    raw_data_json = Column(JSON, nullable=True)     # Raw debug data
    notified_guilds_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class BotStateORM(Base):
    __tablename__ = 'bot_state'
    
    key = Column(String(100), primary_key=True)
    value = Column(String(255))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
