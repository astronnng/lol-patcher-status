import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from bot.database.models import Base, GuildConfigORM, PatchRecordORM
from bot.database.repository import Repository
from datetime import datetime

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

@pytest.mark.asyncio
async def test_guild_config_crud(db):
    repo = Repository(db)
    
    # Create
    await repo.update_guild_config(12345, 67890, 111)
    
    # Read
    config = await repo.get_guild_config(12345)
    assert config is not None
    assert config.guild_id == 12345
    assert config.channel_id == 67890
    assert config.ping_role_id == 111
    
    # Update
    await repo.update_guild_config(12345, 999)
    config = await repo.get_guild_config(12345)
    assert config.channel_id == 999
    
    # Unsubscribe
    await repo.unsubscribe_guild(12345)
    config = await repo.get_guild_config(12345)
    assert config.enabled == 0

@pytest.mark.asyncio
async def test_database_save_and_retrieve_patch(db):
    repo = Repository(db)
    
    # Save
    await repo.add_patch_record("14.12", [{"champion_name": "Ahri", "summary": "buff"}], [], [])
    
    # Verify processed
    is_processed = await repo.is_patch_processed("14.12")
    assert is_processed is True
    
    # Retrieve record
    record = await repo.get_patch_record_orm("14.12")
    assert record.version == "14.12"
    assert record.buffs_json[0]['champion_name'] == "Ahri"

@pytest.mark.asyncio
async def test_bot_state_persistence(db):
    repo = Repository(db)
    await repo.set_bot_state("last_checked", "14.12")
    val = await repo.get_bot_state("last_checked")
    assert val == "14.12"
    
    # Update
    await repo.set_bot_state("last_checked", "14.13")
    val = await repo.get_bot_state("last_checked")
    assert val == "14.13"
