from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QFormLayout, QLineEdit,
                             QHBoxLayout, QPushButton, QMessageBox)

from model.company_model import CompanyModel
from session import Session
from presentation.view import funzioni_utili
from presentation.controller.credential_controller import ControllerAutenticazione


class VistaStatoAzienda(QMainWindow):
    def __init__(self, callback):
        super().__init__()

        self.callback = callback
        self.controller = ControllerAutenticazione()
        azienda : CompanyModel = self.controller.get_user()
        

        # Elementi di layout
        self.id_azienda_label = QLabel("ID")
        self.id_azienda_input = QLineEdit(str(azienda.Id_azienda))

        self.nome_label = QLabel("Nome")
        self.nome_input = QLineEdit(str(azienda.Nome))

        self.tipo_label = QLabel("Tipo")
        self.tipo_input = QLineEdit(str(azienda.Tipo))

        self.co2_consumata_totale_label = QLabel("CO2 consumata totale")
        self.co2_consumata_totale_input = QLineEdit(str(azienda.Co2_consumata))

        self.co2_risparmiata_totale_label = QLabel("CO2 risparmiata totale")
        self.co2_risparmiata_totale_input = QLineEdit(str(azienda.Co2_compensata)) 

        self.token_label = QLabel("Token accumulati")
        self.token_label_input = QLineEdit(str(azienda.Token)) 

        self.conferma_button = QPushButton('Conferma modifiche')

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

        welcome_label = QLabel('Informazioni azienda')
        funzioni_utili.insert_label(welcome_label, main_layout)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        form_container = QVBoxLayout()
        form_container.addLayout(form_layout)
        form_container.setContentsMargins(150, 0, 150, 0)

        self.id_azienda_input.setReadOnly(True)
        funzioni_utili.add_field_to_form(self.id_azienda_label, self.id_azienda_input, form_layout)

        self.nome_input.setReadOnly(True)
        # self.nome_input.setValidator(QRegExpValidator(QRegExp("[A-Za-z0-9 ]+")))  # Nome con lettere e numeri
        funzioni_utili.add_field_to_form(self.nome_label, self.nome_input, form_layout)

        self.tipo_input.setReadOnly(True)
        funzioni_utili.add_field_to_form(self.tipo_label, self.tipo_input, form_layout)


        if Session().current_user["role"] != "Certificatore":
            self.co2_consumata_totale_input.setReadOnly(True)
            funzioni_utili.add_field_to_form(self.co2_consumata_totale_label, self.co2_consumata_totale_input,
                                             form_layout)

            self.co2_risparmiata_totale_input.setReadOnly(True)
            funzioni_utili.add_field_to_form(self.co2_risparmiata_totale_label, self.co2_risparmiata_totale_input,
                                             form_layout)
            
            self.token_label_input.setReadOnly(True)
            funzioni_utili.add_field_to_form(self.token_label, self.token_label_input,
                                             form_layout)
            


        main_layout.addLayout(form_container)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)


        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def on_conferma_button_clicked(self):
        id_azienda = self.id_azienda_input.text()
        nome = self.nome_input.text()
        tipo = self.tipo_input.text()

        #self.aggiungi(id_azienda, nome, tipo, indirizzo)

    def aggiungi(self, id_azienda, nome, tipo, indirizzo):
        QMessageBox.information(self, "SupplyChain",
                                f"Dati azienda modificati correttamente:\n"
                                f"ID Azienda: {id_azienda}\n"
                                f"Nome: {nome}\n"
                                f"Tipo: {tipo}\n"
                                f"Indirizzo: {indirizzo}")
        self.callback((id_azienda, id_azienda, tipo, indirizzo, nome))
        self.close()
