import sys
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen

from view.vista_accedi import VistaAccedi

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = QSplashScreen(QPixmap("images/logo_splash.png"), Qt.WindowStaysOnTopHint)
    splash.show()
    time.sleep(1)
    finestra = VistaAccedi()
    finestra.show()
    splash.finish(finestra)
    sys.exit(app.exec())
