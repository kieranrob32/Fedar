import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw
from typing import Optional

from src.core.window import FedarWindow
from src.core.logger import logger
from src.styles import load_styles


def create_app() -> Adw.Application:
    logger.debug("Creating Fedar application")
    
    try:
        app = Adw.Application(
            application_id='com.fedar.app',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        
        logger.debug("Loading application styles")
        load_styles()
        
        def on_activate(app: Adw.Application) -> None:
            logger.info("Application activated")
            try:
                win = FedarWindow(app)
                win.present()
                logger.debug("Main window created and presented")
            except Exception as e:
                logger.error(f"Failed to create main window: {e}")
                raise
        
        app.connect('activate', on_activate)
        logger.info("Application created successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


def main() -> None:
    logger.info("Starting Fedar application")
    try:
        app = create_app()
        logger.debug("Running application main loop")
        app.run(None)
    except KeyboardInterrupt:
        logger.warning("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        raise
