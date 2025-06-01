# src/pkm_app/core/application/use_cases/note_link/__init__.py
"""
Casos de uso para la entidad NoteLink.
"""

from .create_note_link_use_case import CreateNoteLinkUseCase
from .delete_note_link_use_case import DeleteNoteLinkUseCase
from .get_note_link_use_case import GetNoteLinkUseCase
from .list_note_links_use_case import ListNoteLinksUseCase
from .update_note_link_use_case import UpdateNoteLinkUseCase

__all__ = [
    "CreateNoteLinkUseCase",
    "DeleteNoteLinkUseCase",
    "GetNoteLinkUseCase",
    "ListNoteLinksUseCase",
    "UpdateNoteLinkUseCase",
]
