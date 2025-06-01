# src/pkm_app/tests/conftest.py
import asyncio
import sys

if sys.platform == "win32":
    # Cambiar a SelectorEventLoopPolicy en Windows para intentar resolver
    # problemas con ProactorEventLoop y asyncpg/SQLAlchemy al cerrar conexiones.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
