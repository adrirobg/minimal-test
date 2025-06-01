import logging
import os
import sys
import uuid
from collections.abc import Iterator

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

# Ajusta según la ubicación real de tu archivo models.py
# Add current working directory to path
# The following sys.path manipulation is removed as it's preferable
# for Mypy and Pytest to be configured to find packages in 'src' directory directly
# (e.g. via mypy_path = "src" in pyproject.toml and pytest's src-layout support).
# sys.path.append(os.getcwd())
from src.pkm_app.infrastructure.persistence.sqlalchemy.models import (
    Keyword,
    Note,
    NoteLink,
    Project,
    UserProfile,
)

# Cargar variables de entorno del archivo .env
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la DATABASE_URL
DATABASE_URL_FROM_ENV = os.getenv("DATABASE_URL")
if not DATABASE_URL_FROM_ENV:
    raise ValueError(
        "DATABASE_URL no encontrada en el entorno. Asegúrate de que .env está configurado."
    )

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

if not all([db_user, db_password, db_host, db_port, db_name]):
    raise ValueError("Faltan variables de BD (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME).")

SYNC_DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
logger.info(f"Usando base de datos real: {SYNC_DATABASE_URL}")


@pytest_asyncio.fixture(scope="session")
def engine() -> Engine:
    """Crea un engine de SQLAlchemy para toda la sesión de tests."""
    # Usar una base de datos de test separada si es posible, ej. agregando _test al nombre
    logger.info(f"Current working directory: {os.getcwd()}")
    return create_engine(
        SYNC_DATABASE_URL, echo=False
    )  # echo=False para no ensuciar output de tests


@pytest_asyncio.fixture(scope="session")
def tables(engine: Engine) -> Iterator[None]:
    logger.info(
        f"Checking for __init__.py in src/pkm_app: " f"{os.path.exists('src/pkm_app/__init__.py')}"
    )
    logger.info(
        f"Checking for __init__.py in src/pkm_app/infrastructure: "
        f"{os.path.exists('src/pkm_app/infrastructure/__init__.py')}"
    )
    logger.info(
        f"Checking for __init__.py in src/pkm_app/infrastructure/persistence: "
        f"{os.path.exists('src/pkm_app/infrastructure/persistence/__init__.py')}"
    )
    logger.info(
        f"Checking for __init__.py in src/pkm_app/infrastructure/persistence/sqlalchemy: "
        f"{os.path.exists('src/pkm_app/infrastructure/persistence/sqlalchemy/__init__.py')}"
    )
    """
    Crea todas las tablas antes de que comiencen los tests y las elimina después.
    Se ejecuta una vez por sesión de tests.
    """
    logger.info("NO se crean ni eliminan tablas (usando base de datos real).")
    yield
    logger.info("NO se crean ni eliminan tablas (usando base de datos real).")


@pytest_asyncio.fixture(scope="session")
def db_session(engine: Engine, tables: None) -> Iterator[SQLAlchemySession]:
    """
    Proporciona una sesión de base de datos transaccional para cada test.
    Los cambios se revierten después de cada test.
    """
    connection = engine.connect()
    # Iniciar una transacción
    trans = connection.begin()

    # Crear una fábrica de sesiones vinculada a la conexión
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    logger.info("Sesión de base de datos (transaccional) creada para el test.")

    yield session

    # Revertir la transacción y cerrar la sesión/conexión
    session.close()
    trans.rollback()
    connection.close()
    logger.info("Sesión de base de datos (transaccional) cerrada y cambios revertidos.")


def test_database_connection(engine: Engine) -> None:
    """Prueba la conexión básica a la base de datos."""
    try:
        connection = engine.connect()
        logger.info("Conexión a la base de datos para test_database_connection exitosa.")
        connection.close()
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos durante test_database_connection: {e}")
        pytest.fail(f"Error al conectar a la base de datos: {e}")


def test_models_operations(db_session: SQLAlchemySession) -> None:
    """
    Prueba las operaciones CRUD básicas en los modelos SQLAlchemy.
    Utiliza la sesión transaccional `db_session`.
    """
    # --- Test UserProfile ---
    logger.info("\n--- Probando UserProfile ---")
    test_user_id = f"test_user_{uuid.uuid4()}"
    logger.info(f"Creando usuario con ID: {test_user_id}")
    new_user = UserProfile(
        user_id=test_user_id,
        name="Test User Pytest",
        email=f"{test_user_id}@example.com",
        preferences={"theme": "light"},
    )
    db_session.add(new_user)
    db_session.commit()  # Commit para que el ID se genere y esté disponible
    db_session.refresh(new_user)
    logger.info(f"Usuario creado: {new_user}")

    fetched_user = db_session.get(UserProfile, test_user_id)
    assert fetched_user is not None
    assert fetched_user.name == "Test User Pytest"
    logger.info(f"Usuario recuperado: {fetched_user}")

    # --- Test Project (asociado al usuario) ---
    logger.info("\n--- Probando Project ---")
    new_project = Project(user_id=test_user_id, name="Proyecto de Prueba Pytest")
    db_session.add(new_project)
    db_session.commit()
    db_session.refresh(new_project)
    logger.info(f"Proyecto creado: {new_project}")
    assert new_project.user_id == test_user_id

    # --- Test Note (asociada al usuario y proyecto) ---
    logger.info("\n--- Probando Note ---")
    new_note = Note(
        user_id=test_user_id,
        project_id=new_project.id,
        title="Mi Primera Nota Pytest",
        content="Este es el contenido de la nota de prueba con Pytest.",
        type="TestNotePytest",
    )
    db_session.add(new_note)
    db_session.commit()
    db_session.refresh(new_note)
    logger.info(f"Nota creada: {new_note}")
    assert new_note.user_id == test_user_id
    assert new_note.project_id == new_project.id

    # --- Test Keyword y relación Note-Keyword ---
    logger.info("\n--- Probando Keyword y relación Note-Keyword ---")
    keyword1_name = f"pytest_tag_{uuid.uuid4()}"
    keyword2_name = f"sqlalchemy_tag_{uuid.uuid4()}"

    # Las keywords se crean si no existen o se recuperan si ya existen (por user_id, name)
    keyword1 = db_session.query(Keyword).filter_by(user_id=test_user_id, name=keyword1_name).first()
    if not keyword1:
        keyword1 = Keyword(user_id=test_user_id, name=keyword1_name)
        db_session.add(keyword1)

    keyword2 = db_session.query(Keyword).filter_by(user_id=test_user_id, name=keyword2_name).first()
    if not keyword2:
        keyword2 = Keyword(user_id=test_user_id, name=keyword2_name)
        db_session.add(keyword2)

    db_session.commit()  # Para asegurar que los keywords tengan ID si son nuevos
    if keyword1.id:
        db_session.refresh(keyword1)  # Solo refrescar si tiene ID (fue añadido/comiteado)
    if keyword2.id:
        db_session.refresh(keyword2)

    # Asignar keywords a la nota
    new_note.keywords.append(keyword1)
    new_note.keywords.append(keyword2)
    db_session.commit()
    db_session.refresh(new_note)
    logger.info(
        f"Nota '{new_note.title}' ahora tiene keywords: {[kw.name for kw in new_note.keywords]}"
    )
    assert len(new_note.keywords) >= 2

    # --- Test NoteLink ---
    logger.info("\n--- Probando NoteLink ---")
    note2 = Note(
        user_id=test_user_id,
        title="Segunda Nota para Enlace Pytest",
        content="Contenido de la segunda nota con Pytest.",
        type="TestNotePytest",
    )
    db_session.add(note2)
    db_session.commit()
    db_session.refresh(note2)

    new_link = NoteLink(
        source_note_id=new_note.id,
        target_note_id=note2.id,
        link_type="related_pytest_test",
        user_id=test_user_id,
    )
    db_session.add(new_link)
    db_session.commit()
    db_session.refresh(new_link)
    logger.info(f"Enlace creado: {new_link}")

    # Consultar los enlaces de la primera nota
    db_session.refresh(new_note)  # Refrescar para cargar las relaciones
    logger.info(f"Enlaces desde '{new_note.title}':")
    found_link = False
    for link in new_note.source_of_links:
        logger.info(f"  -> Tipo: {link.link_type}, Destino: {link.target_note.title}")
        if link.target_note_id == note2.id:
            found_link = True
    assert found_link

    logger.info("\n¡Pruebas de modelos SQLAlchemy con Pytest completadas con éxito!")


# No se necesita if __name__ == "__main__": unittest.main() con pytest
# pytest descubrirá y ejecutará las funciones test_* automáticamente.
#
# Comentario sobre Base.metadata.create_all(engine) y drop_all(engine):
# Esto ahora se maneja con la fixture `tables` a nivel de sesión.
# Si se usa una base de datos de test dedicada (ej. postgresql.../test_db),
# esto asegura que las tablas se crean al inicio y se eliminan al final de la sesión de tests.
# Cada test individual opera dentro de una transacción que se revierte,
# por lo que los datos no persisten entre tests.
