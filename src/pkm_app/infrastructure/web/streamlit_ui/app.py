import logging

import streamlit as st

from pkm_app.core.application.use_cases.note.create_note_use_case import CreateNoteUseCase
from pkm_app.core.application.use_cases.note.list_notes_use_case import ListNotesUseCase
from pkm_app.infrastructure.config.settings import get_settings
from pkm_app.infrastructure.persistence.sqlalchemy.unit_of_work import SQLAlchemyUnitOfWork
from pkm_app.logging_config import configure_logging

# Configuración inicial
configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


def main() -> None:
    """Función principal de la aplicación Streamlit."""
    st.set_page_config(page_title="Kairos BCP - PKM", page_icon="📝", layout="wide")

    st.title("Kairos BCP - Sistema de Gestión de Conocimiento Personal")

    # Inicializar Unit of Work
    uow = SQLAlchemyUnitOfWork(settings.DATABASE_URL)

    # Sección para listar notas
    st.header("Mis Notas")
    with st.spinner("Cargando notas..."):
        notes = ListNotesUseCase(uow).execute()
        for note in notes:
            st.write(f"**{note.title}**")
            st.write(note.content[:100] + "...")

    # Sección para crear nueva nota
    st.header("Nueva Nota")
    with st.form("new_note_form"):
        title = st.text_input("Título")
        content = st.text_area("Contenido")
        submitted = st.form_submit_button("Guardar")

        if submitted:
            try:
                CreateNoteUseCase(uow).execute(title=title, content=content)
                st.success("Nota creada exitosamente!")
            except Exception as e:
                logger.error(f"Error al crear nota: {e}")
                st.error(f"Error al crear nota: {e}")


if __name__ == "__main__":
    main()
