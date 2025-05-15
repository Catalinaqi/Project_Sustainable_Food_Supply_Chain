# pylint: disable=no-name-in-module
# pylint: disable=import-error

from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt
from presentation.controller.company_controller import ControllerAzienda
from session import Session
from model.threshold_model import ThresholdModel


class SoglieAziendaView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.tipo_azienda: str = Session().current_user.get("role", "")
        self.controller = ControllerAzienda()

        self.soglie: list[ThresholdModel] = self.controller.lista_soglie()  # Mock data
        self.soglie_filtrate: list[ThresholdModel] = self.soglie.copy()

        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<b>Soglie dell'azienda:</b> {self.tipo_azienda}"))

        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Filtra soglie...")
        self.filtro_input.textChanged.connect(self.filtra_soglie)
        layout.addWidget(self.filtro_input)

        self.tabella = QTableWidget()
        self.tabella.setColumnCount(4)
        self.tabella.setHorizontalHeaderLabels(["Operazione", "Prodotto", "Soglia CO2", "Tipo"])
        self.tabella.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabella.setSortingEnabled(True)

        layout.addWidget(self.tabella)
        self.setWindowTitle("Operazioni Azienda")

        self.aggiorna_tabella()

    def filtra_soglie(self, testo: str) -> None:
        testo = testo.lower()
        self.soglie_filtrate = [
            op for op in self.soglie
            if testo in op.tipo.lower() or testo in op.prodotto.lower() or testo in str(op.soglia_massima).lower()
        ]
        self.aggiorna_tabella()

    def aggiorna_tabella(self) -> None:
        self.tabella.setRowCount(len(self.soglie_filtrate))

        for row, op in enumerate(self.soglie_filtrate):
            self.tabella.setItem(row, 0, QTableWidgetItem(op.tipo))
            self.tabella.setItem(row, 1, QTableWidgetItem(op.prodotto))

            try:
                soglia = float(op.soglia_massima)
                item_co2 = QTableWidgetItem(f"{soglia:.2f}")
                item_co2.setData(Qt.UserRole, soglia)  # Sorting numerico corretto
            except (ValueError, TypeError) as err:
                print(f"[ERRORE parsing soglie]: {err} su {op.soglia_massima}")
                item_co2 = QTableWidgetItem(str(op.soglia_massima))
            self.tabella.setItem(row, 2, item_co2)

            self.tabella.setItem(row, 3, QTableWidgetItem(op.tipo))
