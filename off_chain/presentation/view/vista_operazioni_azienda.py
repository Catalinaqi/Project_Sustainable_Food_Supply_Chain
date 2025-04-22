from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton
)
from PyQt5.QtCore import Qt

from model.operation_estesa_model import OperazioneEstesaModel 
from presentation.view.vista_composizione_prodotto import VistaCreaProdottoTrasformato
from presentation.controller.company_controller import ControllerAzienda
from presentation.view.vista_aggiungi_operazione import AggiungiOperazioneView
from session import Session


class OperazioniAziendaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.id_azienda : int = Session().current_user["id_azienda"]
        self.role = Session().current_user["role"]
        self.controller = ControllerAzienda()
        

        self.operazioni : list[OperazioneEstesaModel]= self.controller.lista_operazioni(self.id_azienda) # Mock data
        self.operazioni_filtrate = self.operazioni.copy()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"<b>Operazioni dell'azienda:</b> {self.id_azienda}"))

        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Filtra operazioni...")
        self.filtro_input.textChanged.connect(self.filtra_operazioni)
        layout.addWidget(self.filtro_input)

        self.tabella = QTableWidget()
        self.tabella.setColumnCount(3)
        self.tabella.setHorizontalHeaderLabels(["Tipo", "Data", "Dettagli"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setSortingEnabled(True)

        layout.addWidget(self.tabella)
        self.setLayout(layout)

        self.aggiorna_tabella()
        self.setWindowTitle("Operazioni Azienda")

        self.bottone_aggiungi = QPushButton("Aggiungi Operazione")
        self.bottone_aggiungi.clicked.connect(self.apri_aggiungi_operazione)
        layout.addWidget(self.bottone_aggiungi)

    def filtra_operazioni(self, testo):
        testo = testo.lower()
        self.operazioni_filtrate = [
            op for op in self.operazioni
            if testo in op.Nome_operazione.lower() or testo in op.Nome_prodotto.lower()
        ]
        self.aggiorna_tabella()

    def aggiorna_tabella(self):
        self.tabella.setRowCount(len(self.operazioni_filtrate))

        for row, op in enumerate(self.operazioni_filtrate):
            self.tabella.setItem(row, 0, QTableWidgetItem(op.Nome_operazione))
            self.tabella.setItem(row, 1, QTableWidgetItem(op.Nome_prodotto))

    def apri_aggiungi_operazione(self):
        if Session().current_user["role"] == "Trasformatore":
            self.finestra_aggiungi = VistaCreaProdottoTrasformato(self)
        else:
            self.finestra_aggiungi = AggiungiOperazioneView(self)

        self.finestra_aggiungi.operazione_aggiunta.connect(self.ricarica_operazioni)
        self.finestra_aggiungi.exec_()  



    def ricarica_operazioni(self):
        self.operazioni = self.controller.lista_operazioni(self.id_azienda)
        self.filtra_operazioni(self.filtro_input.text())

