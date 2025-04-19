from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit
)
from PyQt5.QtCore import Qt
from model.product_model import ProductModel
from session import Session
from presentation.controller.company_controller import ControllerAzienda


class VisualizzaMagazzinoView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()
        #self.id_azienda = Session().current_user["id_azienda"]

        #self.prodotti_magazzino_completi = self.controller.get_prodotti_magazzino(self.id_azienda)

        self.prodotti_magazzino_completi = [
            ProductModel(1, "Prodotto A", []),
            ProductModel(2, "Prodotto B", []),
            ProductModel(3, "Prodotto C", []),
        ]

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Magazzino Azienda")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Prodotti disponibili nel magazzino:"))

        # Campo di filtro per nome
        self.input_filtro_nome = QLineEdit()
        self.input_filtro_nome.setPlaceholderText("Filtra per nome prodotto...")
        self.input_filtro_nome.textChanged.connect(self.filtra_prodotti)
        layout.addWidget(self.input_filtro_nome)

        # Tabella
        self.tabella_magazzino = QTableWidget()
        self.tabella_magazzino.setColumnCount(4)
        self.tabella_magazzino.setHorizontalHeaderLabels([
            "Nome Prodotto", "Categoria", "Quantità Disponibile", "Unità di Misura"
        ])
        self.tabella_magazzino.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.tabella_magazzino)
        self.setLayout(layout)
        self.resize(600, 400)

        self.filtra_prodotti()

    def filtra_prodotti(self):
        testo = self.input_filtro_nome.text().lower().strip()
        prodotti_filtrati : list[ProductModel]= [
            p for p in self.prodotti_magazzino_completi
            if testo in p.Nome_prodotto.lower()
        ]
        self.mostra_prodotti(prodotti_filtrati)

    def mostra_prodotti(self, prodotti : list[ProductModel]):
        self.tabella_magazzino.setRowCount(len(prodotti))
        for row, prodotto in enumerate(prodotti):
            self.tabella_magazzino.setItem(row, 0, QTableWidgetItem(prodotto.Id_prodotto))
            self.tabella_magazzino.setItem(row, 1, QTableWidgetItem(prodotto.Nome_prodotto))
            self.tabella_magazzino.setItem(row, 2, QTableWidgetItem(str(100)))  # Placeholder per la quantità disponibile
            self.tabella_magazzino.setItem(row, 3, QTableWidgetItem("kg"))  # Placeholder per l'unità di misura
