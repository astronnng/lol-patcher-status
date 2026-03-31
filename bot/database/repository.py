from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .models import GuildConfigORM, PatchRecordORM, BotStateORM
from typing import Optional, List
from datetime import datetime

class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Guild Configs
    async def get_guild_config(self, guild_id: int) -> Optional[GuildConfigORM]:
        stmt = select(GuildConfigORM).where(GuildConfigORM.guild_id == guild_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_guild_config(self, guild_id: int, channel_id: int, ping_role_id: int = None, enabled: bool = True):
        config = await self.get_guild_config(guild_id)
        if config:
            config.channel_id = channel_id
            config.ping_role_id = ping_role_id
            config.enabled = 1 if enabled else 0
        else:
            config = GuildConfigORM(guild_id=guild_id, channel_id=channel_id, ping_role_id=ping_role_id, enabled=1)
            self.session.add(config)
        await self.session.commit()
        return config

    async def unsubscribe_guild(self, guild_id: int):
        stmt = update(GuildConfigORM).where(GuildConfigORM.guild_id == guild_id).values(enabled=0)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_active_guild_configs(self) -> List[GuildConfigORM]:
        stmt = select(GuildConfigORM).where(GuildConfigORM.enabled == 1)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # Patch Records
    async def get_patch_record(self, version: str) -> Optional[PatchRecordORM]:
        stmt = select(PatchRecordORM).where(PatchRecordORM.version == version)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_latest_patch_record(self) -> Optional[PatchRecordORM]:
        stmt = select(PatchRecordORM).order_by(PatchRecordORM.created_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add_patch_record(self, version: str, buffs: list, nerfs: list, adjusts: list, raw_data: dict = None):
        record = PatchRecordORM(
            version=version,
            detected_at=datetime.utcnow(),
            buffs_json=buffs,
            nerfs_json=nerfs,
            adjustments_json=adjusts,
            raw_data_json=raw_data
        )
        self.session.add(record)
        await self.session.commit()
        return record

    async def is_patch_processed(self, version: str) -> bool:
        record = await self.get_patch_record(version)
        return record is not None

    # Bot State
    async def get_bot_state(self, key: str) -> Optional[str]:
        stmt = select(BotStateORM).where(BotStateORM.key == key)
        result = await self.session.execute(stmt)
        state = result.scalars().first()
        return state.value if state else None

    async def set_bot_state(self, key: str, value: str):
        stmt = select(BotStateORM).where(BotStateORM.key == key)
        result = await self.session.execute(stmt)
        state = result.scalars().first()
        if state:
            state.value = value
        else:
            state = BotStateORM(key=key, value=value)
            self.session.add(state)
        await self.session.commit()
