# src/pkm_app/infrastructure/persistence/migrations/env.py
import os
from logging.config import fileConfig

from alembic import context

# --- Importar python-dotenv para cargar el archivo .env ---
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL

# --- ¡¡¡IMPORTANTE!!! ---
# Importa tu objeto 'Base' de SQLAlchemy desde donde lo hayas definido.
# Ajusta la ruta de importación según la estructura de tu proyecto.
# Esta es la Base a la que están asociados todos tus modelos SQLAlchemy.
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import Base

# --- Carga de configuración de Alembic y logging ---
config = context.config

# Interpreta el archivo de configuración para el logging de Python (si existe).
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Configuración de Metadata para 'autogenerate' ---
# Asigna la metadata de tu Base a target_metadata.
# Alembic usará esto para detectar cambios en tus modelos y generar migraciones.
target_metadata = Base.metadata

# --- Configuración de la URL de la Base de Datos ---
# Carga las variables de entorno desde el archivo .env
load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
# Para 'DB_HOST', si ejecutas 'poetry run alembic' desde tu máquina host
# y la base de datos está en Docker, usa 'localhost'.
# Si Alembic se ejecutara DENTRO de un contenedor Docker en la misma red que la DB,
# usarías el nombre del servicio Docker (ej. 'db').
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

if not all([db_user, db_password, db_host, db_port, db_name]):
    raise ValueError(
        "Faltan variables de entorno para la base de datos en .env: "
        "DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME."
    )

# Construye la URL de conexión SÍNCRONA para Alembic (usando psycopg2)
# Alembic opera de forma síncrona.
s_db_url = URL.create(
    drivername="postgresql+psycopg2",  # Driver síncrono
    username=db_user,
    password=db_password,
    host=db_host,
    port=int(db_port),
    database=db_name,
)

# Establece la opción en la configuración de Alembic que será usada por alembic.ini
# (referenciada como %(DB_CONNECTION_STRING)s en alembic.ini)
config.set_main_option("DB_CONNECTION_STRING", s_db_url.render_as_string(hide_password=False))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("DB_CONNECTION_STRING")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Necesario para que autogenerate funcione correctamente con tipos como UUID de PostgreSQL
        # y otros constraints o tipos específicos.
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # engine_from_config lee la sección [alembic] de alembic.ini,
    # busca 'sqlalchemy.url', que a su vez usa %(DB_CONNECTION_STRING)s.
    # engine_from_config lee la sección [alembic] de alembic.ini,
    # busca 'sqlalchemy.url', que a su vez usa %(DB_CONNECTION_STRING)s.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",  # Asegúrate que alembic.ini tenga sqlalchemy.url = %(DB_CONNECTION_STRING)s
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Necesario para que autogenerate funcione correctamente
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
