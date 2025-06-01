import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

# --- Keyword Schemas ---


class KeywordBase(BaseModel):
    """
    Base schema for keyword data.
    """

    name: str = Field(..., min_length=1, description="The name of the keyword. Must not be empty.")

    model_config = ConfigDict(
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_name_not_empty(cls, data) -> Any:
        if isinstance(data, dict) and "name" in data:
            name = data["name"]
            if isinstance(name, str) and not name.strip():
                raise ValueError("El nombre de la keyword no puede estar vacío.")
        return data


class KeywordCreate(KeywordBase):
    """
    Schema for creating a new keyword.
    Inherits 'name' from KeywordBase.
    user_id will be assigned by the application logic.
    """

    pass


class KeywordUpdate(BaseModel):
    """
    Schema for updating an existing keyword.
    'name' is optional.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        description="The new name of the keyword. If provided, must not be empty.",
    )

    model_config = ConfigDict(
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_name_not_empty(cls, data) -> Any:
        if isinstance(data, dict) and "name" in data:
            name = data["name"]
            if name is not None and isinstance(name, str):
                if not name.strip():
                    raise ValueError("El nombre de la keyword no puede estar vacío.")
                # Update the data to the stripped version
                data["name"] = name.strip()
        return data


class KeywordSchema(KeywordBase):
    """
    Schema representing a keyword, including database-generated fields.
    This schema is typically used for responses.
    """

    id: uuid.UUID = Field(description="Unique identifier for the keyword.")
    user_id: str = Field(description="Identifier of the user who owns this keyword.")
    created_at: datetime = Field(description="Timestamp of when the keyword was created.")

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating from ORM models
        frozen=True,  # Make instances immutable after creation
        extra="forbid",
    )
