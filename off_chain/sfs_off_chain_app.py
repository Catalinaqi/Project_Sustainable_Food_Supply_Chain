import sys
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen
from configuration.log_load_setting import logger
from database.db_migrations import DatabaseMigrations
from configuration.database import Database
from session import Session
from presentation.view.vista_accedi import VistaAccedi
from PyQt5.QtWidgets import QApplication



def setup_database():

    try:
        DatabaseMigrations.run_migrations()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)  # Stops the application if there is a critical error


if __name__ == "__main__":
    # Configure the database before starting the graphical interface
    setup_database()
    # Starting the PyQt application
    app = QApplication(sys.argv)
    logger.info("Frontend: Starting the PyQt application...")

    session = Session()
    logger.info(f"Start session on  {session.start_app}")

    # Show Splash Screen
    splash = QSplashScreen(QPixmap("presentation/resources/logo_splash.png"), Qt.WindowStaysOnTopHint)
    splash.show()
    time.sleep(1)    
    finestra = VistaAccedi()
    finestra.show()
    splash.finish(finestra)
    sys.exit(app.exec())
