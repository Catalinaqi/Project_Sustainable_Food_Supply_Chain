from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMessageBox

from off_chain.controllers.controller_azienda import ControllerAzienda
from off_chain.view import funzioni_utili
from off_chain.view.vista_stato_azienda import VistaStatoAzienda
from off_chain.view.vista_azioni_compensative import VistaAzioniCompensative
from off_chain.view.vista_operazioni import VistaOperazioni
from off_chain.view.vista_soglie import VistaSoglie
from off_chain.view.vista_sviluppatori import VistaSviluppatori


class HomePage(QMainWindow):
    def __init__(self, callback, utente):
        super().__init__()

        self.controller = ControllerAzienda()

        self.vista_soglie = None
        self.vista_sviluppatori = None
        self.stato = None
        self.vista_azioni = None
        self.vista_operazioni = None
        self.utente = utente

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
        self.welcome_label = QLabel(f"Ciao {self.utente[3]} 👋!\nBenvenuto in SupplyChain.\n"
                                    f"Prego selezionare un'opzione dal menu")
        self.button_operazioni = QPushButton('Operazioni')
        self.button_azioni_compensative = QPushButton('Azioni compensative')
        self.button_soglie = QPushButton('Soglie CO2')
        self.button_stato_azienda = QPushButton('Stato azienda')
        self.button_token = QPushButton('Gestione token')
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

        funzioni_utili.insert_label(self.welcome_label, main_layout)

        button_layout = QGridLayout()
        button_layout.setSpacing(1)

        funzioni_utili.insert_button_in_grid(self.button_operazioni, button_layout, 1, 2)
        self.button_operazioni.clicked.connect(self.show_operazioni)

        funzioni_utili.insert_button_in_grid(self.button_azioni_compensative, button_layout, 1, 4)
        self.button_azioni_compensative.clicked.connect(self.show_azioni)

        funzioni_utili.insert_button_in_grid(self.button_soglie, button_layout, 3, 1)
        self.button_soglie.clicked.connect(self.show_soglie)

        funzioni_utili.insert_button_in_grid(self.button_stato_azienda, button_layout, 3, 5)
        self.button_stato_azienda.clicked.connect(self.show_stato)

        funzioni_utili.insert_button_in_grid(self.button_token, button_layout, 5, 2)
        self.button_token.clicked.connect(self.show_token)

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
            self, 'SupplyChain', "Tutorial work in progress")

    def faq(self):
        QMessageBox.information(
            self, 'SupplyChain', "FAQ work in progress")

    def tcu(self):
        QMessageBox.information(
            self, 'SupplyChain', "Termini e condizioni d'uso work in progress")

    def show_operazioni(self):
        self.vista_operazioni = VistaOperazioni(self.controller, self.utente)
        self.vista_operazioni.show()

    def show_azioni(self):
        self.vista_azioni = VistaAzioniCompensative(self.utente)
        self.vista_azioni.show()

    def show_stato(self):
        self.stato = VistaStatoAzienda(self.aggiorna_profilo, self.utente, self.controller)
        self.stato.show()

    def aggiorna_profilo(self, utente):
        self.utente = utente
        self.welcome_label.setText(
            f"Ciao {utente[4]} 👋!\nBenvenuto in SupplyChain.\n"
            f"Prego selezionare un'opzione dal menu"
        )

    def show_sviluppatori(self):
        self.vista_sviluppatori = VistaSviluppatori()
        self.vista_sviluppatori.show()

    def show_token(self):
        QMessageBox.information(
            self, 'SupplyChain', "Gestione token work in progress work in progress")

    def show_soglie(self):
        self.vista_soglie = VistaSoglie()
        self.vista_soglie.show()
