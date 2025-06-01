# src/pkm_app/logging_config.py
import logging.config
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # Permite configurar el nivel general desde .env

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # Mantener loggers existentes (ej. de librerías)
    "formatters": {
        "simple": {
            "format": "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "verbose": {
            "format": "%(asctime)s - [%(levelname)s] - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(process)d-%(thread)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",  # Envía logs a la consola (stderr por defecto)
            "formatter": "simple",  # Usa el formato 'simple'
            "level": LOG_LEVEL,  # Nivel mínimo para este handler
            "stream": "ext://sys.stdout",  # Envía a stdout en lugar de stderr
        },
        # Puedes añadir más handlers aquí en el futuro, como FileHandler:
        # "file": {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "formatter": "verbose",
        #     "filename": "kairos_bcp_app.log", # Nombre del archivo de log
        #     "maxBytes": 1024 * 1024 * 5,  # 5 MB
        #     "backupCount": 5, # Número de archivos de log a mantener
        #     "level": "INFO",
        # },
    },
    "loggers": {
        "pkm_app": {  # Logger específico para tu aplicación
            "handlers": ["console"],  # Hacia dónde enviar los logs de 'pkm_app'
            "level": LOG_LEVEL,
            "propagate": False,  # Evita que los logs de 'pkm_app' se pasen al logger root si ya los manejaste
        },
        "sqlalchemy": {  # Logger específico para SQLAlchemy
            "handlers": ["console"],
            # Nivel INFO para ver queries, DEBUG para queries + resultados de filas
            # En producción, querrás subirlo a WARNING o ERROR.
            "level": "WARNING",  # Por defecto, para no ser muy verboso
            "propagate": False,
        },
        "uvicorn": {  # Logger para el servidor Uvicorn
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "fastapi": {  # Logger para FastAPI
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # Puedes añadir más loggers específicos aquí
    },
    "root": {  # Configuración para el logger raíz (fallback)
        "handlers": [
            "console"
        ],  # Hacia dónde enviar los logs que no son capturados por loggers específicos
        "level": "WARNING",  # Nivel por defecto para el logger raíz
    },
}


def setup_logging() -> None:
    """Aplica la configuración de logging."""
    logging.config.dictConfig(LOGGING_CONFIG)
    # logger = logging.getLogger(__name__)
    # logger.info("Sistema de logging configurado.")


# Si quieres que el logging se configure al importar este módulo:
# setup_logging()

# En el punto de entrada de tu aplicación (ej. tu script principal de Streamlit),
# importa setup_logging y llámalo una vez:
# from src.pkm_app.logging_config import setup_logging; setup_logging().
# En cualquier otro módulo donde necesites logs:
# import logging; logger = logging.getLogger(__name__)
# y luego usa logger.info(), logger.debug(), logger.error(), etc.

""" Para una aplicación Streamlit: Lo harías al principio de tu script principal de Streamlit.

Python

# tu_app_streamlit.py
from src.pkm_app.logging_config import setup_logging # Asegúrate de que la ruta de importación sea correcta

setup_logging() # Configura el logging ANTES de hacer otras cosas

import streamlit as st
import logging

logger = logging.getLogger(__name__) # Obtén un logger para este script de Streamlit

logger.info("Aplicación Streamlit iniciada y logging configurado.")
st.write("Bienvenido a Kairos BCP!")
# ... resto de tu app Streamlit ... """

""" Una vez que setup_logging() ha sido llamado, la configuración está activa para toda la aplicación. En cualquier otro módulo de tu proyecto (core/services.py, infrastructure/persistence/repositories.py, etc.) donde quieras emitir logs, haces lo siguiente:

Python

# Ejemplo en: src/pkm_app/core/some_service.py
import logging

# Obtén un logger para este módulo.
# Usar __name__ es una convención que crea un logger con el nombre jerárquico del módulo,
# ej. "pkm_app.core.some_service". Esto es útil porque en LOGGING_CONFIG
# definiste un logger para "pkm_app", y sus hijos heredarán su configuración (handlers, nivel)
# a menos que se especifique lo contrario.
logger = logging.getLogger(__name__)

class MiServicio:
    def hacer_algo_importante(self, dato):
        logger.debug(f"Recibido dato para procesar: {dato}")
        try:
            if dato is None:
                logger.warning("El dato recibido es None, se procederá con valor por defecto.")
                # ... lógica con valor por defecto ...

            # ... procesamiento ...
            resultado = f"Procesado: {dato}"
            logger.info(f"Dato procesado exitosamente. Resultado: {resultado}")
            return resultado
        except Exception as e:
            logger.error(f"Ocurrió un error al procesar el dato '{dato}'. Error: {e}", exc_info=True)
            # exc_info=True añade la información de la traza de la excepción al log.
            raise # Es buena práctica relanzar la excepción o manejarla apropiadamente. """
