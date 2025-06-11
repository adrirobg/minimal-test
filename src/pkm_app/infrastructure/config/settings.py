import os
from typing import cast

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Componentes individuales de la URL de la base de datos
    # Estos valores se cargarán desde el archivo .env o las variables de entorno del sistema.
    DB_USER: str = os.environ.get("DB_USER", "")
    DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "")
    DB_HOST: str = os.environ.get("DB_HOST", "")
    DB_PORT: int = int(os.environ.get("DB_PORT", 5432))
    DB_NAME: str = os.environ.get("DB_NAME", "")

    # Variable original para compatibilidad o usos directos si es necesario
    # Esta plantilla utilizará los valores de DB_USER, DB_PASSWORD, etc., cargados desde el entorno.
    DATABASE_URL_TEMPLATE: str = (
        "postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    )

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", case_sensitive=False, env_file_encoding="utf-8"
    )

    @computed_field  # type: ignore[misc]
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # Construye la URL asíncrona usando los componentes individuales
        # Esto asegura que los valores correctos de .env se usen.
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                path=f"{self.DB_NAME}",
            )
        )

    @computed_field  # type: ignore[misc]
    @property
    def SYNC_DATABASE_URL(self) -> str:
        # Construye la URL síncrona para Alembic
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg2",  # Usamos psycopg2 para Alembic
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                path=f"{self.DB_NAME}",
            )
        )


settings = Settings()

# Para depuración, puedes imprimir las URLs generadas:
# print(f"ASYNC_DATABASE_URL: {settings.ASYNC_DATABASE_URL}")
# print(f"SYNC_DATABASE_URL: {settings.SYNC_DATABASE_URL}")
