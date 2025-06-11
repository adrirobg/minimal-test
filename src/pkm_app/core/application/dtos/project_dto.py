import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# --- Project Schemas ---


class ProjectBase(BaseModel):
    """
    Base schema for project data.
    """

    name: str = Field(..., min_length=1, description="The name of the project. Must not be empty.")
    description: str | None = Field(default=None, description="A description of the project.")
    parent_project_id: uuid.UUID | None = Field(
        default=None, description="ID of the parent project, if this is a sub-project."
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.
    Inherits fields from ProjectBase.
    user_id will be assigned by the application logic.
    """

    pass


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.
    All fields are optional.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        description="The new name of the project. If provided, must not be empty.",
    )
    description: str | None = Field(default=None, description="The new description of the project.")
    parent_project_id: uuid.UUID | None = Field(
        default=None, description="The new parent project ID."
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class ProjectSchema(ProjectBase):
    """
    Schema representing a project, including database-generated fields.
    This schema is typically used for responses.
    """

    id: uuid.UUID = Field(description="Unique identifier for the project.")
    user_id: str = Field(description="Identifier of the user who owns this project.")
    created_at: datetime = Field(description="Timestamp of when the project was created.")
    updated_at: datetime = Field(description="Timestamp of the last update to the project.")
    # Relationships like child_projects or a fully resolved parent_project
    # are typically handled by specific use cases or separate queries
    # to avoid overly complex default schemas.

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating from ORM models
        frozen=True,  # Make instances immutable after creation
        extra="forbid",
    )
