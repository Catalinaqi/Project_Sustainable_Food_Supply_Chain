from PyQt5.QtCore import Qt, QRegExp, QDate
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QFormLayout, QLineEdit,
                             QHBoxLayout, QPushButton, QMessageBox, QDateEdit)

from off_chain.presentation.controller.company_controller import ControllerAzienda
from off_chain.presentation.view import funzioni_utili


class VistaInserisciAzione(QMainWindow):
    def __init__(self, callback, azienda):
        super().__init__()

        self.callback = callback
        self.azienda = azienda

        self.controller = ControllerAzienda()

        # Elementi di layout
        self.data_label = QLabel("Data")
        self.data_input = QDateEdit()

        self.azienda_label = QLabel("Azienda")
        self.azienda_input = QLineEdit(str(self.azienda[3]))

        self.co2_compensata_label = QLabel("CO2 compensata")
        self.co2_compensata_input = QLineEdit()

        self.descrizione_label = QLabel("Descrizione azione compensativa")
        self.descrizione_input = QLineEdit()

        self.conferma_button = QPushButton('Conferma')

        self.setWindowIcon(QIcon("presentation\\resources\\logo_centro.png"))

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)  # Centra verticalmente

        welcome_label = QLabel('Completa i seguenti campi')
        funzioni_utili.insert_label(welcome_label, main_layout)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        form_container = QVBoxLayout()
        form_container.addLayout(form_layout)
        form_container.setContentsMargins(150, 0, 150, 0)

        self.azienda_input.setReadOnly(True)
        funzioni_utili.add_field_to_form(self.azienda_label, self.azienda_input, form_layout)

        self.co2_compensata_input.setValidator(
            QRegExpValidator(QRegExp(r"^\d+(\.\d{1,})?$")))  # Per la CO2 compensata (solo numeri)
        funzioni_utili.add_field_to_form(self.co2_compensata_label, self.co2_compensata_input, form_layout)

        self.descrizione_input.setValidator(
            QRegExpValidator(QRegExp("[A-Za-z0-9 ]+")))  # Descrizione (solo lettere e numeri)
        funzioni_utili.add_field_to_form(self.descrizione_label, self.descrizione_input, form_layout)

        self.data_input.setCalendarPopup(True)
        self.data_input.setDisplayFormat("dd/MM/yyyy")
        self.data_input.setDate(QDate.currentDate())
        funzioni_utili.add_field_to_form(self.data_label, self.data_input, form_layout)

        main_layout.addLayout(form_container)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        funzioni_utili.insert_button(self.conferma_button, button_layout)
        self.conferma_button.clicked.connect(self.on_conferma_button_clicked)

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def on_conferma_button_clicked(self):
        azienda = self.azienda[0]
        co2_compensata = self.co2_compensata_input.text()
        descrizione = self.descrizione_input.text()
        data = self.data_input.text()

        self.aggiungi(azienda, co2_compensata, descrizione, data)

    def aggiungi(self, azienda, co2_compensata, descrizione, data):
        self.controller.aggiungi_azione(data, azienda, co2_compensata, descrizione)
        QMessageBox.information(self, "SupplyChain",
                                "Azione compensativa inserita correttamente!")
        self.callback()
        self.close()
