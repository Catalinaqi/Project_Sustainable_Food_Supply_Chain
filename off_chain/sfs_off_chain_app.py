import sys
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen

from configuration.log_load_setting import logger
from session import Session
from presentation.view.vista_accedi import VistaAccedi


def setup_database():

    try:
        pass
        #DatabaseMigrations.run_migrations()
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

    # Close the database connection when the app closes
    # app.aboutToQuit.connect(DatabaseConnectionSetting.close_connection)



import sys
from PyQt5.QtWidgets import QApplication
from model.product_model import ProductModel, Componente
from model.operation_model import OperationModel
from presentation.view.vista_operazioni_azienda import OperazioniAziendaView

# Fake data per test

# Avvia l'app per test manuale

"""
if __name__ == "__main__":
    app = QApplication(sys.argv)




    finestra = OperazioniAziendaView()



    finestra.show()
    sys.exit(app.exec_())"""
