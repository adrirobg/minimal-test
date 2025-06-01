import pytest
import os
import sys  # Añadido para manipular sys.modules
from unittest import mock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Mockear las variables de entorno antes de que database.py las cargue
DEFAULT_ENV_VARS = {
    "DB_USER": "test_user",
    "DB_PASSWORD": "test_password",
    "DB_HOST": "test_host",
    "DB_PORT": "1234",
    "DB_NAME": "test_db",
}


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mockea las variables de entorno para todos los tests en este módulo."""
    for key, value in DEFAULT_ENV_VARS.items():
        monkeypatch.setenv(key, value)
    # Mockear load_dotenv a nivel global para todos los tests que importen 'database'
    # Esto debe hacerse antes de la primera importación de 'database'
    monkeypatch.setattr("dotenv.load_dotenv", lambda: None)


@pytest.fixture
def mock_sqlalchemy_creators(monkeypatch):
    """Mockea create_async_engine y async_sessionmaker."""
    mock_engine_creator = mock.MagicMock()
    monkeypatch.setattr("sqlalchemy.ext.asyncio.create_async_engine", mock_engine_creator)

    mock_session_maker_creator_func = mock.MagicMock(spec=async_sessionmaker)

    # Lo que async_sessionmaker(...) devuelve (el callable AsyncSessionLocal)
    mock_async_session_local_callable = mock.Mock(spec=async_sessionmaker)  # spec para el callable

    # Lo que AsyncSessionLocal() devuelve (la instancia de sesión)
    mock_async_session_instance = mock.AsyncMock(spec=AsyncSession)
    # Configurar __aenter__ para que devuelva la propia instancia de sesión mockeada
    mock_async_session_instance.__aenter__.return_value = mock_async_session_instance

    # Asegurar que los métodos a ser awaited sean AsyncMocks
    mock_async_session_instance.rollback = mock.AsyncMock()
    mock_async_session_instance.close = mock.AsyncMock()

    mock_async_session_local_callable.return_value = mock_async_session_instance
    mock_session_maker_creator_func.return_value = mock_async_session_local_callable

    monkeypatch.setattr(
        "sqlalchemy.ext.asyncio.async_sessionmaker", mock_session_maker_creator_func
    )

    return (
        mock_engine_creator,
        mock_session_maker_creator_func,
        mock_async_session_local_callable,
        mock_async_session_instance,
    )


def import_database_module():
    """
    Importa y devuelve el módulo database.
    Se asegura de que se recargue si ya está en sys.modules para aplicar mocks
    o reflejar cambios en el entorno (ej. variables de entorno eliminadas).
    """
    import importlib

    module_name = "pkm_app.infrastructure.persistence.sqlalchemy.database"

    # Los mocks (dotenv, sqlalchemy) deben ser aplicados por las fixtures ANTES de llamar esta función.

    if module_name in sys.modules:
        # Si el módulo ya fue importado, lo recargamos.
        reloaded_module = importlib.reload(sys.modules[module_name])
    else:
        # Si es la primera vez en este contexto (ej. después de del sys.modules[module_name]), lo importamos.
        reloaded_module = importlib.import_module(module_name)
    return reloaded_module


def test_database_url_construction(monkeypatch):
    """Verifica que ASYNC_DATABASE_URL se construye correctamente."""
    # monkeypatch.setattr ya se encarga de mockear load_dotenv en mock_env_vars
    database = import_database_module()

    expected_url = URL.create(
        drivername="postgresql+asyncpg",
        username=DEFAULT_ENV_VARS["DB_USER"],
        password=DEFAULT_ENV_VARS["DB_PASSWORD"],
        host=DEFAULT_ENV_VARS["DB_HOST"],
        port=int(DEFAULT_ENV_VARS["DB_PORT"]),
        database=DEFAULT_ENV_VARS["DB_NAME"],
    ).render_as_string(hide_password=False)

    assert database.ASYNC_DATABASE_URL == expected_url


def test_missing_env_vars_raises_value_error(monkeypatch):
    """Verifica que se lanza ValueError si faltan variables de entorno."""
    module_name = "pkm_app.infrastructure.persistence.sqlalchemy.database"

    # Eliminar todas las variables de entorno relevantes
    for var in DEFAULT_ENV_VARS.keys():
        monkeypatch.delenv(var, raising=False)

    # Asegurarse de que el módulo database no esté usando una versión cacheada
    # que podría haber leído las variables de entorno antes de que las elimináramos.
    if module_name in sys.modules:
        del sys.modules[module_name]

    with pytest.raises(ValueError, match="Faltan variables de entorno para la base de datos"):
        # La importación (y por tanto la comprobación de env vars) ocurre aquí.
        # Como lo eliminamos de sys.modules, import_database_module lo importará "de nuevo".
        import_database_module()


def test_async_engine_creation(mock_sqlalchemy_creators, monkeypatch):
    """Verifica que create_async_engine se llama con la URL y echo=True."""
    mock_engine_creator, _, _, _ = mock_sqlalchemy_creators

    # Importar el módulo DESPUÉS de que mock_sqlalchemy_creators haya aplicado los mocks
    database_module = import_database_module()

    mock_engine_creator.assert_called_once_with(database_module.ASYNC_DATABASE_URL, echo=True)


def test_async_session_local_creation(mock_sqlalchemy_creators, monkeypatch):
    """Verifica que async_sessionmaker se llama con los parámetros correctos."""
    mock_engine_creator, mock_session_maker_creator_func, _, _ = mock_sqlalchemy_creators

    # El engine que create_async_engine (mockeado) "devolvería"
    # Necesitamos que el mock_engine_creator.return_value sea algo,
    # ya que database.py lo usa como 'bind'
    mock_created_engine = mock.MagicMock()
    mock_engine_creator.return_value = mock_created_engine

    # Importar el módulo DESPUÉS de que los mocks estén listos
    import_database_module()

    mock_session_maker_creator_func.assert_called_once_with(
        bind=mock_created_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest.mark.asyncio
async def test_get_async_db_session_success(mock_sqlalchemy_creators, monkeypatch):
    """Verifica que get_async_db_session proporciona y cierra una sesión."""
    _, _, mock_callable_session_local, mock_session_instance = mock_sqlalchemy_creators

    database_module = import_database_module()

    # Sobrescribir AsyncSessionLocal en el módulo 'database_module' importado
    # con nuestro callable mockeado.
    monkeypatch.setattr(database_module, "AsyncSessionLocal", mock_callable_session_local)

    retrieved_session = None
    # Usar el get_async_db_session del módulo importado
    async for s in database_module.get_async_db_session():
        retrieved_session = s
        # s es el resultado de mock_session_instance.__aenter__()
        # que hemos configurado para que sea mock_session_instance
        assert s is mock_session_instance

    assert retrieved_session is not None
    mock_callable_session_local.assert_called_once()
    mock_session_instance.__aenter__.assert_called_once()
    mock_session_instance.close.assert_called_once()
    mock_session_instance.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_get_async_db_session_exception_rollbacks_and_closes(
    mock_sqlalchemy_creators, monkeypatch
):
    """Verifica que la sesión hace rollback y se cierra en caso de excepción."""
    _, _, mock_callable_session_local, mock_session_instance = mock_sqlalchemy_creators

    database_module = import_database_module()
    monkeypatch.setattr(database_module, "AsyncSessionLocal", mock_callable_session_local)

    custom_exception = ValueError("Test Exception")

    agen = database_module.get_async_db_session()

    # Consumir el generador hasta el primer yield para obtener la sesión
    s = await agen.__anext__()
    assert s is mock_session_instance

    # Ahora, inyectar la excepción en el generador
    # Esto debería ser capturado por el bloque `except Exception:` en `get_async_db_session`
    with pytest.raises(ValueError, match="Test Exception"):
        await agen.athrow(custom_exception)

    # Cuando athrow propaga una excepción fuera del generador, este se cierra automáticamente.
    # No se necesita una llamada explícita a agen.aclose() en este caso específico,
    # a menos que el generador manejara la excepción de athrow y continuara con StopAsyncIteration.

    # Verificaciones
    mock_callable_session_local.assert_called_once()
    mock_session_instance.__aenter__.assert_called_once()

    # El rollback y close deben ser llamados por la lógica explícita
    # en los bloques except y finally de get_async_db_session
    mock_session_instance.rollback.assert_called_once()
    mock_session_instance.close.assert_called_once()


@pytest.fixture
def mock_sqlalchemy_sync_creators(monkeypatch):
    """Mockea create_engine y sessionmaker para la configuración síncrona."""
    mock_sync_engine_creator = mock.MagicMock(spec=create_engine)
    monkeypatch.setattr("sqlalchemy.create_engine", mock_sync_engine_creator)

    mock_sync_session_maker_creator_func = mock.MagicMock(spec=sessionmaker)

    mock_sync_session_local_callable = mock.Mock(spec=sessionmaker)
    mock_sync_session_instance = mock.MagicMock(spec=Session)

    # Configurar el comportamiento de la sesión mockeada
    mock_sync_session_instance.rollback = mock.MagicMock()
    mock_sync_session_instance.close = mock.MagicMock()

    mock_sync_session_local_callable.return_value = mock_sync_session_instance
    mock_sync_session_maker_creator_func.return_value = mock_sync_session_local_callable

    monkeypatch.setattr("sqlalchemy.orm.sessionmaker", mock_sync_session_maker_creator_func)

    return (
        mock_sync_engine_creator,
        mock_sync_session_maker_creator_func,
        mock_sync_session_local_callable,
        mock_sync_session_instance,
    )


def test_sync_database_url_construction(monkeypatch):
    """Verifica que SYNC_DATABASE_URL_STR se construye correctamente."""
    database = import_database_module()

    expected_url = URL.create(
        drivername="postgresql+psycopg2",
        username=DEFAULT_ENV_VARS["DB_USER"],
        password=DEFAULT_ENV_VARS["DB_PASSWORD"],
        host=DEFAULT_ENV_VARS["DB_HOST"],
        port=int(DEFAULT_ENV_VARS["DB_PORT"]),
        database=DEFAULT_ENV_VARS["DB_NAME"],
    ).render_as_string(hide_password=False)

    assert database.SYNC_DATABASE_URL_STR == expected_url


def test_sync_engine_creation(mock_sqlalchemy_sync_creators, monkeypatch):
    """Verifica que create_engine se llama con la URL y echo=True."""
    mock_sync_engine_creator, _, _, _ = mock_sqlalchemy_sync_creators

    database_module = import_database_module()

    mock_sync_engine_creator.assert_called_once_with(
        database_module.SYNC_DATABASE_URL_STR, echo=True
    )


def test_sync_session_local_creation(mock_sqlalchemy_sync_creators, monkeypatch):
    """Verifica que sessionmaker se llama con los parámetros correctos."""
    mock_sync_engine_creator, mock_sync_session_maker_creator_func, _, _ = (
        mock_sqlalchemy_sync_creators
    )

    mock_created_sync_engine = mock.MagicMock()
    mock_sync_engine_creator.return_value = mock_created_sync_engine

    import_database_module()

    mock_sync_session_maker_creator_func.assert_called_once_with(
        autocommit=False, autoflush=False, bind=mock_created_sync_engine, class_=Session
    )


def test_get_sync_db_session_success(mock_sqlalchemy_sync_creators, monkeypatch):
    """Verifica que get_sync_db_session proporciona y cierra una sesión síncrona."""
    _, _, mock_callable_sync_session_local, mock_sync_session_instance = (
        mock_sqlalchemy_sync_creators
    )

    database_module = import_database_module()
    monkeypatch.setattr(database_module, "SyncSessionLocal", mock_callable_sync_session_local)

    retrieved_session = None
    with database_module.get_sync_db_session() as s:
        retrieved_session = s
        assert s is mock_sync_session_instance

    assert retrieved_session is not None
    mock_callable_sync_session_local.assert_called_once()
    mock_sync_session_instance.close.assert_called_once()
    mock_sync_session_instance.rollback.assert_not_called()


def test_get_sync_db_session_exception_rollbacks_and_closes(
    mock_sqlalchemy_sync_creators, monkeypatch
):
    """Verifica que la sesión síncrona hace rollback y se cierra en caso de excepción."""
    _, _, mock_callable_sync_session_local, mock_sync_session_instance = (
        mock_sqlalchemy_sync_creators
    )

    database_module = import_database_module()
    monkeypatch.setattr(database_module, "SyncSessionLocal", mock_callable_sync_session_local)

    custom_exception = ValueError("Test Sync Exception")

    with pytest.raises(ValueError, match="Test Sync Exception"):
        with database_module.get_sync_db_session() as s:
            assert s is mock_sync_session_instance
            raise custom_exception

    mock_callable_sync_session_local.assert_called_once()
    mock_sync_session_instance.rollback.assert_called_once()
    mock_sync_session_instance.close.assert_called_once()
