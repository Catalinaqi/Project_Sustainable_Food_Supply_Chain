from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QDateEdit
)
from PyQt5.QtCore import pyqtSignal, QDate

from model.operation_model import OperationModel
from presentation.controller.company_controller import ControllerAzienda


class AggiungiOperazioneView(QDialog):
    operazione_aggiunta = pyqtSignal()

    def __init__(self, id_azienda, parent=None):
        super().__init__(parent)
        self.id_azienda = id_azienda
        self.controller = ControllerAzienda()
        self.initUI()
        print(f"ID Azienda: {self.id_azienda}")

    def initUI(self):
        self.setWindowTitle("Aggiungi Operazione")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tipo operazione:"))
        self.input_tipo = QLineEdit()
        layout.addWidget(self.input_tipo)

        layout.addWidget(QLabel("Data:"))
        self.input_data = QDateEdit()
        self.input_data.setDate(QDate.currentDate())
        self.input_data.setCalendarPopup(True)
        layout.addWidget(self.input_data)

        layout.addWidget(QLabel("Dettagli:"))
        self.input_dettagli = QTextEdit()
        layout.addWidget(self.input_dettagli)

        self.btn_salva = QPushButton("Salva operazione")
        self.btn_salva.clicked.connect(self.salva_operazione)
        layout.addWidget(self.btn_salva)

        self.setLayout(layout)

        self.resize(400, 300)
        self.raise_()
        self.activateWindow()


    def salva_operazione(self):
        tipo = self.input_tipo.text()
        data = self.input_data.date().toString("yyyy-MM-dd")
        dettagli = self.input_dettagli.toPlainText()

        if tipo.strip():
            nuova_op = OperationModel(tipo, data, dettagli)
            self.controller.aggiungi_operazione(self.id_azienda, nuova_op)
            self.operazione_aggiunta.emit()
            self.close()
