from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit
)
from model.materia_prima_model import MateriaPrimaModel
from presentation.controller.company_controller import ControllerAzienda


class VisualizzaMagazzinoView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()

        self.prodotti_magazzino_completi : list[MateriaPrimaModel] = self.controller.get_materie_prime_magazzino_azienda()

       

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
        prodotti_filtrati : list[MateriaPrimaModel]= [
            p for p in self.prodotti_magazzino_completi
            if testo in p.nome.lower()
        ]
        self.mostra_prodotti(prodotti_filtrati)

    def mostra_prodotti(self, prodotti : list[MateriaPrimaModel]):
        self.tabella_magazzino.setRowCount(len(prodotti))
        for row, prodotto in enumerate(prodotti):
            self.tabella_magazzino.setItem(row, 0, QTableWidgetItem(prodotto.nome))
            self.tabella_magazzino.setItem(row, 1, QTableWidgetItem(prodotto.id_prodotto))
            self.tabella_magazzino.setItem(row, 2, QTableWidgetItem(str(prodotto.quantita))) # Placeholder per la quantità disponibile
            self.tabella_magazzino.setItem(row, 3, QTableWidgetItem("kg"))  # Placeholder per l'unità di misura
