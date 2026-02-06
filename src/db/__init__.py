from src.db.connection import initialize_indexes


async def ensure_indexes():
    """Call once at server startup before accepting traffic.

    Idempotent — safe to call on every boot. Creates vector + fulltext
    indexes and runs any pending data migrations.
    """
    await initialize_indexes()
