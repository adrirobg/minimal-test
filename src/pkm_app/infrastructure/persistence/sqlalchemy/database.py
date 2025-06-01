import os
from collections.abc import AsyncGenerator, Iterator
from contextlib import contextmanager  # Añadido

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

# Cargar variables de entorno desde el archivo .env
# Esto asegura que las variables de DB_USER, DB_PASSWORD, etc., estén disponibles.
load_dotenv()

# Construir la URL de la base de datos asíncrona desde las variables de entorno
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")  # 'localhost' si la app corre en el host y DB en Docker
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError(
        "Faltan variables de entorno para la base de datos en .env: "
        "DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME."
    )

# URL para SQLAlchemy con asyncpg
ASYNC_DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
).render_as_string(
    hide_password=False
)  # hide_password=False para que esté completa la URL

# Crear el motor asíncrono de SQLAlchemy
# echo=True es útil para desarrollo para ver las sentencias SQL generadas.
# Considera ponerlo en False o controlarlo con una variable de entorno para producción.
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Crear una fábrica de sesiones asíncronas (SessionLocal)
# Esta fábrica se usará para crear nuevas instancias de AsyncSession.
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Común para evitar problemas con objetos desasociados después del commit
    autoflush=False,  # Control manual del flush para operaciones asíncronas
    autocommit=False,  # Control manual del commit
)


# (Opcional, para uso futuro con FastAPI o gestión de dependencias)
# Función para obtener una sesión de base de datos de manera asíncrona.
# Esto es un patrón común para la inyección de dependencias en FastAPI.
async def get_async_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Dependency that provides an asynchronous database session.
    Ensures the session is closed after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Opcional: await session.commit() si quieres un commit automático aquí,
            # aunque usualmente el commit se maneja en la lógica de negocio/repositorio.
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# --- Configuración Síncrona (para scripts, Alembic, tareas que no requieren async) ---

SYNC_DATABASE_URL_STR = URL.create(
    drivername="postgresql+psycopg2",  # Driver síncrono
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
).render_as_string(hide_password=False)

sync_engine = create_engine(SYNC_DATABASE_URL_STR, echo=True)  # echo=True para desarrollo

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    class_=Session,  # Usando la clase correcta de sqlalchemy.orm
)


@contextmanager
def get_sync_db_session() -> Iterator[Session]:
    """
    Dependency that provides a synchronous database session.
    Ensures the session is closed after use.
    """
    db = SyncSessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# NOTA: La Base declarativa (Base = declarative_base()) que usan tus modelos SQLAlchemy
# ya está definida en tu archivo `src/pkm_app/infrastructure/persistence/sqlalchemy/models.py`.
# No necesitas redefinirla aquí. El engine que hemos creado se usará con esa Base
# cuando interactúes con los modelos a través de una sesión creada con AsyncSessionLocal.
