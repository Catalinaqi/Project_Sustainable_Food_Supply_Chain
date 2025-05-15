# pylint: disable=no-name-in-module
# pylint: disable=import-error
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QGroupBox, QHeaderView, QInputDialog
)

from presentation.view.vista_richiesta_prodotto import RichiestaProdottoView
from session import Session
from presentation.controller.company_controller import ControllerAzienda
from model.richiesta_model import RichiestaModel


class VisualizzaRichiesteView(QDialog):
    """View per visualizzare e gestire le richieste aziendali."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()
        self.richieste_ricevute: list[RichiestaModel] = self.controller.get_richieste_ricevute()
        self.richieste_effettuate: list[RichiestaModel] = self.controller.get_richieste_effettuate()
        self.init_ui()

    def init_ui(self) -> None:
        """Inizializza l'interfaccia grafica."""
        self.setWindowTitle("Gestione Richieste")
        layout = QVBoxLayout()
        current_role = Session().current_user["role"]
        headers = [
            "Azienda Destinataria", "Prodotto", "Quantità",
            "Stato Ricevente", "Stato Trasportatore", "Data"
        ]

        # Sezione richieste ricevute (escluso ruolo Rivenditore)
        if current_role != "Rivenditore":
            group_ricevute = QGroupBox("Richieste Ricevute")
            layout_ricevute = QVBoxLayout()

            self.tabella_ricevute = QTableWidget()
            self.tabella_ricevute.setColumnCount(len(headers))
            self.tabella_ricevute.setHorizontalHeaderLabels(headers)
            self.tabella_ricevute.setSelectionBehavior(QTableWidget.SelectRows)
            self.tabella_ricevute.setSelectionMode(QTableWidget.SingleSelection)
            self.tabella_ricevute.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tabella_ricevute.horizontalHeader().setStretchLastSection(True)
            self.tabella_ricevute.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
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

        # Sezione richieste effettuate (per Trasformatore e Rivenditore)
        if current_role in ("Trasformatore", "Rivenditore"):
            group_effettuate = QGroupBox("Richieste Effettuate")
            layout_effettuate = QVBoxLayout()

            self.tabella_effettuate = QTableWidget()
            self.tabella_effettuate.setColumnCount(len(headers))
            self.tabella_effettuate.setHorizontalHeaderLabels(headers)
            self.tabella_effettuate.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tabella_effettuate.horizontalHeader().setStretchLastSection(True)
            self.tabella_effettuate.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            layout_effettuate.addWidget(self.tabella_effettuate)
            group_effettuate.setLayout(layout_effettuate)
            layout.addWidget(group_effettuate)

            self.carica_effettuate()

            self.bottone_aggiungi = QPushButton("Invia Richiesta")
            self.bottone_aggiungi.clicked.connect(self.apri_invia_richiesta)
            layout.addWidget(self.bottone_aggiungi)

        self.carica_ricevute()
        self.setLayout(layout)
        self.resize(1000, 700)

    def carica_ricevute(self) -> None:
        """Carica i dati delle richieste ricevute nella tabella."""
        self.tabella_ricevute.setRowCount(len(self.richieste_ricevute))
        for row, richiesta in enumerate(self.richieste_ricevute):
            self.tabella_ricevute.setItem(row, 0, QTableWidgetItem(richiesta.nome_azienda_richiedente))
            self.tabella_ricevute.setItem(row, 1, QTableWidgetItem(richiesta.nome_prodotto))
            self.tabella_ricevute.setItem(row, 2, QTableWidgetItem(str(richiesta.quantita)))
            self.tabella_ricevute.setItem(row, 3, QTableWidgetItem(richiesta.stato_ricevente))
            self.tabella_ricevute.setItem(row, 4, QTableWidgetItem(richiesta.stato_trasportatore))
            self.tabella_ricevute.setItem(row, 5, QTableWidgetItem(str(richiesta.data)))

    def carica_effettuate(self) -> None:
        """Carica i dati delle richieste effettuate nella tabella."""
        self.richieste_effettuate = self.controller.get_richieste_effettuate()
        self.tabella_effettuate.setRowCount(len(self.richieste_effettuate))
        for row, richiesta in enumerate(self.richieste_effettuate):
            self.tabella_effettuate.setItem(row, 0,\
                                             QTableWidgetItem(richiesta.nome_azienda_ricevente))
            self.tabella_effettuate.setItem(row, 1,\
                                             QTableWidgetItem(richiesta.nome_prodotto))
            self.tabella_effettuate.setItem(row, 2,\
                                             QTableWidgetItem(str(richiesta.quantita)))
            self.tabella_effettuate.setItem(row, 3,\
                                             QTableWidgetItem(richiesta.stato_ricevente))
            self.tabella_effettuate.setItem(row, 4,\
                                             QTableWidgetItem(richiesta.stato_trasportatore))
            self.tabella_effettuate.setItem(row, 5,\
                                             QTableWidgetItem(str(richiesta.data)))

    def accetta_richiesta(self) -> None:
        """Accetta la richiesta selezionata."""
        self._gestisci_richiesta("Accettata")

    def rifiuta_richiesta(self) -> None:
        """Rifiuta la richiesta selezionata."""
        self._gestisci_richiesta("Rifiutata")

    def _gestisci_richiesta(self, nuovo_stato: str) -> None:
        """
        Gestisce l'aggiornamento dello stato di una richiesta.

        Args:
            nuovo_stato (str): Nuovo stato da impostare alla richiesta.
        """
        row = self.tabella_ricevute.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Attenzione", "Seleziona una richiesta.")
            return
        richiesta = self.richieste_ricevute[row]
        current_role = Session().current_user["role"]

        if current_role == "Trasportatore":
            if richiesta.stato_trasportatore != "In attesa":
                QMessageBox.information(self, "Info", "Questa richiesta è già stata gestita.")
                return

            co2, ok = QInputDialog.getDouble(
                self,
                "CO₂ Emessa",
                "Inserisci la quantità di CO₂ emessa (kg):",
                decimals=2
            )
            if not ok:
                return

            try:
                self.controller.salva_operazione_trasporto(
                    id_prodotto=richiesta.id_prodotto,
                    quantita=richiesta.quantita,
                    co2=co2,
                    id_azienda_richiedente= \
                        richiesta.id_azienda_richiedente,
                    id_azienda_ricevente=richiesta.id_azienda_ricevente,
                    id_lotto_input=richiesta.id_lotto_input,
                )
            except Exception as exc:
                QMessageBox.critical(self, "Errore", f"Errore nel salvataggio CO₂: {exc}")
                return

        try:
            self.controller.update_richiesta(
                id_richiesta=richiesta.id_richiesta,
                nuovo_stato=nuovo_stato
            )
            QMessageBox.information(self, "Successo", "Richiesta aggiornata con successo.")
            self.carica_ricevute()
        except Exception as exc:
            QMessageBox.critical(self, "Errore", f"Errore durante la gestione: {exc}")

    def apri_invia_richiesta(self) -> None:
        """Apre la finestra per l'invio di una nuova richiesta."""
        self.finestra_aggiungi = RichiestaProdottoView(self)
        self.finestra_aggiungi.salva_richiesta.connect(self.carica_effettuate)
        self.finestra_aggiungi.exec_()
