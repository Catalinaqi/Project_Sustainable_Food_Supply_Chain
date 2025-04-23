import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLabel, QGroupBox
)
from PyQt5.QtCore import Qt
from presentation.view.vista_richiesta_prodotto import RichiestaProdottoView
from session import Session
from presentation.controller.company_controller import ControllerAzienda


class VisualizzaRichiesteView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()

        #self.id_azienda = Session().current_user["id_azienda"]

        # Carica dati
        #self.richieste_ricevute: list[richiesta] = self.controller.get_richieste_ricevute(self.id_azienda)
        #self.richieste_effettuate : list[richiesta] = self.controller.get_richieste_effettuate(self.id_azienda)

        self.richieste_ricevute: list[richiesta] = []

        self.richieste_effettuate: list[richiesta] = []

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gestione Richieste")

        layout = QVBoxLayout()

        # --- SEZIONE RICEVUTE ---
        group_ricevute = QGroupBox("Richieste Ricevute")
        layout_ricevute = QVBoxLayout()

        self.tabella_ricevute = QTableWidget()
        self.tabella_ricevute.setColumnCount(5)
        self.tabella_ricevute.setHorizontalHeaderLabels([
            "Azienda Richiedente", "Prodotto", "Quantità", "Stato", "Data"
        ])
        self.tabella_ricevute.setSelectionBehavior(self.tabella_ricevute.SelectRows)
        self.tabella_ricevute.setSelectionMode(self.tabella_ricevute.SingleSelection)
        self.tabella_ricevute.setEditTriggers(QTableWidget.NoEditTriggers)

        layout_ricevute.addWidget(self.tabella_ricevute)

        btn_layout = QHBoxLayout()
        self.btn_accetta = QPushButton("Accetta")
        self.btn_rifiuta = QPushButton("Rifiuta")
        self.btn_accetta.clicked.connect(self.accetta_richiesta)
        self.btn_rifiuta.clicked.connect(self.rifiuta_richiesta)
        btn_layout.addWidget(self.btn_accetta)
        btn_layout.addWidget(self.btn_rifiuta)

        layout_ricevute.addLayout(btn_layout)
        group_ricevute.setLayout(layout_ricevute)
        layout.addWidget(group_ricevute)

        # --- SEZIONE EFFETTUATE ---
        group_effettuate = QGroupBox("Richieste Effettuate")
        layout_effettuate = QVBoxLayout()

        self.tabella_effettuate = QTableWidget()
        self.tabella_effettuate.setColumnCount(5)
        self.tabella_effettuate.setHorizontalHeaderLabels([
            "Azienda Destinataria", "Prodotto", "Quantità", "Stato", "Data"
        ])
        self.tabella_effettuate.setEditTriggers(QTableWidget.NoEditTriggers)

        layout_effettuate.addWidget(self.tabella_effettuate)
        group_effettuate.setLayout(layout_effettuate)
        layout.addWidget(group_effettuate)

        # Carica dati
        self.carica_ricevute()
        self.carica_effettuate()

        self.bottone_aggiungi = QPushButton("Invia Richiesta")
        self.bottone_aggiungi.clicked.connect(self.apri_invia_richiesta)
        layout.addWidget(self.bottone_aggiungi)

        self.setLayout(layout)
        self.resize(700, 600)

    def carica_ricevute(self):
        self.tabella_ricevute.setRowCount(len(self.richieste_ricevute))
        for row, richiesta in enumerate(self.richieste_ricevute):
            self.tabella_ricevute.setItem(row, 0, QTableWidgetItem(richiesta.Nome_azienda_richiedente))
            self.tabella_ricevute.setItem(row, 1, QTableWidgetItem(richiesta.Id_prodotto))
            self.tabella_ricevute.setItem(row, 2, QTableWidgetItem(str(richiesta.Quantita)))
            self.tabella_ricevute.setItem(row, 3, QTableWidgetItem(richiesta.Stato))
            self.tabella_ricevute.setItem(row, 4, QTableWidgetItem(str(richiesta.Data)))

    def carica_effettuate(self):
        self.tabella_effettuate.setRowCount(len(self.richieste_effettuate))
        for row, richiesta in enumerate(self.richieste_effettuate):
            self.tabella_effettuate.setItem(row, 0, QTableWidgetItem(richiesta.Id_azienda_destinataria))
            self.tabella_effettuate.setItem(row, 1, QTableWidgetItem(richiesta.Id_prodotto))
            self.tabella_effettuate.setItem(row, 2, QTableWidgetItem(str(richiesta.Quantita)))
            self.tabella_effettuate.setItem(row, 3, QTableWidgetItem(richiesta.Stato))
            self.tabella_effettuate.setItem(row, 4, QTableWidgetItem(str(richiesta.Data)))

    def accetta_richiesta(self):
        self._gestisci_richiesta("Accettata")

    def rifiuta_richiesta(self):
        self._gestisci_richiesta("Rifiutata")

    def _gestisci_richiesta(self, nuovo_stato):
        row = self.tabella_ricevute.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Attenzione", "Seleziona una richiesta.")
            return

        richiesta = self.richieste_ricevute[row]

        if richiesta.Stato != "In attesa":
            QMessageBox.information(self, "Info", "Questa richiesta è già stata gestita.")
            return

        try:
            """self.controller.gestisci_richiesta(
                id_richiesta=richiesta.Id_richiesta,
                nuovo_stato=nuovo_stato
            )"""
            QMessageBox.information(self, "Successo", f"Richiesta  con successo.")

            # Ricarica dati
            #self.richieste_ricevute = self.controller.get_richieste_ricevute(self.id_azienda)
            self.carica_ricevute()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la gestione: {str(e)}")


    def apri_invia_richiesta(self):
        self.finestra_aggiungi = RichiestaProdottoView(self)
        self.finestra_aggiungi.salva_richiesta.connect(self.carica_effettuate)
        self.finestra_aggiungi.exec_()


class richiesta():
    def __init__(self, id_richiesta, id_azienda_richiedente, id_prodotto, quantita, stato, data):
        self.Id_richiesta = id_richiesta
        self.Id_azienda_richiedente = id_azienda_richiedente
        self.Id_azienda_destinataria = 1
        self.Id_prodotto = id_prodotto
        self.Quantita = quantita
        self.Stato = stato
        self.Data : datetime = data
        self.Nome_azienda_richiedente = "Azienda A"