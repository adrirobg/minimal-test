"""
Main entry point for the Kairos BCP PKM application.

This module provides the main entry point and configuration for running
the PKM (Personal Knowledge Management) system.
"""

import logging
import sys
from pathlib import Path

from pkm_app.infrastructure.config.settings import get_settings
from pkm_app.logging_config import configure_logging


def setup_application() -> None:
    """
    Initialize the application with proper configuration.
    
    Sets up logging, validates configuration, and prepares
    the application environment.
    """
    # Configure logging first
    configure_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load and validate settings
        settings = get_settings()
        logger.info("Application configuration loaded successfully")
        logger.info(f"Database URL configured: {settings.DATABASE_URL[:20]}...")
        
        # Validate critical paths and dependencies
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL is required but not configured")
            
        logger.info("Application setup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to setup application: {e}")
        sys.exit(1)


def run_streamlit_ui() -> None:
    """
    Launch the Streamlit user interface.
    
    This is the default UI for the PKM application.
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting Streamlit UI...")
    
    try:
        import streamlit.web.cli as stcli
        import sys
        
        # Path to the Streamlit app
        app_path = Path(__file__).parent / "infrastructure" / "web" / "streamlit_ui" / "app.py"
        
        if not app_path.exists():
            raise FileNotFoundError(f"Streamlit app not found at {app_path}")
        
        # Run Streamlit app
        sys.argv = ["streamlit", "run", str(app_path)]
        stcli.main()
        
    except ImportError:
        logger.error("Streamlit is not installed. Install it with: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start Streamlit UI: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main entry point for the application.
    
    Sets up the application and launches the default interface.
    """
    setup_application()
    
    # For now, default to Streamlit UI
    # In the future, this could support different interfaces:
    # - FastAPI server
    # - CLI interface
    # - etc.
    run_streamlit_ui()


if __name__ == "__main__":
    main()