from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMenu, QMessageBox

from off_chain.controllers.controller_guest import ControllerGuest
from off_chain.view import funzioni_utili
from off_chain.view.vista_aziende import VistaAziende
from off_chain.view.vista_prodotti import VistaProdotti
from off_chain.view.vista_sviluppatori import VistaSviluppatori


class HomePageGuest(QMainWindow):
    def __init__(self, callback):
        super().__init__()

        self.controller = ControllerGuest()

        self.vista_prodotti = None
        self.vista_sviluppatori = None
        self.vista_prodotti_certificati = VistaProdotti(self.controller, filtro_certificazioni=True)
        self.vista_aziende = None

        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet("background-color: rgb(240, 240, 240)")
        funzioni_utili.config_menubar(
            self, "File", QIcon("images\\exit.png"),
            "Logout", 'Ctrl+Q', self.menu_bar
        ).triggered.connect(self.logout)
        funzioni_utili.config_menubar(
            self, "Termini e condizioni d'uso", QIcon("images\\tcu.png"),
            "Leggi i termini e le condizioni d'uso", 'Ctrl+W', self.menu_bar
        ).triggered.connect(self.tcu)
        funzioni_utili.config_menubar(
            self, "FAQ", QIcon("images\\faq.png"),
            "Visualizza le domande più frequenti", 'Ctrl+E', self.menu_bar
        ).triggered.connect(self.faq)
        funzioni_utili.config_menubar(
            self, "Tutorial", QIcon("images\\tutorial.png"),
            "Visualizza tutorial", 'Ctrl+R', self.menu_bar
        ).triggered.connect(self.tutorial)

        self.setWindowIcon(QIcon("images\\logo_centro.png"))

        self.callback = callback

        # Elementi di layout
        self.logo = QLabel()
        self.button_prodotti = QPushButton('Ricerca prodotti')
        self.button_aziende = QPushButton('Aziende')
        self.button_certificazioni = QPushButton('Prodotti certificati')
        self.button_sviluppatori = QPushButton('Sviluppatori')

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(50)
        main_layout.setAlignment(Qt.AlignCenter)

        welcome_label = QLabel("Benvenuto in SupplyChain.\nPrego selezionare un'opzione dal menu")
        funzioni_utili.insert_label(welcome_label, main_layout)

        button_layout = QGridLayout()
        button_layout.setSpacing(1)

        funzioni_utili.insert_button_in_grid(self.button_prodotti, button_layout, 1, 2)
        self.button_prodotti.clicked.connect(self.lista_prodotti_clicked)

        funzioni_utili.insert_button_in_grid(self.button_aziende, button_layout, 1, 4)
        self.button_aziende.clicked.connect(self.show_aziende)

        funzioni_utili.insert_button_in_grid(self.button_certificazioni, button_layout, 5, 2)
        self.button_certificazioni.clicked.connect(self.show_certificati)

        funzioni_utili.insert_button_in_grid(self.button_sviluppatori, button_layout, 5, 4)
        self.button_sviluppatori.clicked.connect(self.show_sviluppatori)

        funzioni_utili.insert_logo(self.logo, button_layout, QPixmap("images\\logo_centro.png"))

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def logout(self):
        # Mostra una finestra di conferma
        reply = QMessageBox.question(
            self,
            "Conferma logout",
            "Sei sicuro di voler effettuare il logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # Procede solo se l'utente clicca "Yes"
        if reply == QMessageBox.Yes:
            self.close()
            self.callback()

    def tutorial(self):
        QMessageBox.information(
            self, 'SupplyChain', 'Tutorial work in progress')

    def faq(self):
        QMessageBox.information(
            self, 'SupplyChain', "FAQ work in progress")

    def tcu(self):
        QMessageBox.information(
            self, 'SupplyChain', "Termini e condizioni d'uso work in progress")

    def lista_prodotti_clicked(self):
        self.vista_prodotti = VistaProdotti(self.controller)
        self.vista_prodotti.show()

    def show_aziende(self):
        self.vista_aziende = VistaAziende()
        self.vista_aziende.show()

    def show_sviluppatori(self):
        self.vista_sviluppatori = VistaSviluppatori()
        self.vista_sviluppatori.show()

    def show_certificati(self):
        self.vista_prodotti_certificati.show()
