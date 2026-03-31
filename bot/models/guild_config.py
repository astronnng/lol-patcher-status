from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class GuildConfig(Base):
    __tablename__ = 'guild_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<GuildConfig(guild_id={self.guild_id}, channel_id={self.channel_id})>"
