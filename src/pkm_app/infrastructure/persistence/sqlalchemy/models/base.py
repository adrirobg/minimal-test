from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

# Se recomienda usar un MetaData con un esquema de nombrado para constraints
# para evitar colisiones de nombres y facilitar las migraciones con Alembic.
# https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata_obj


# --- Función para el default de UUID si se genera en Python ---
def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


# Common columns that can be inherited or used as mixins if desired
# For now, keeping them directly in models for clarity, but this is an option:
# class TimestampMixin:
#     created_at: Mapped[datetime] = mapped_column(
#         TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
#     )
#     updated_at: Mapped[datetime] = mapped_column(
#         TIMESTAMP(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now(),
#         nullable=False,
#     )
