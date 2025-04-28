from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem
)
import sys
import os

# Ottieni il percorso assoluto della cartella 'a'
percorso_a = os.path.abspath(os.path.join(__file__, "../../model"))

# Aggiungi 'a' al path di ricerca dei moduli
sys.path.append(percorso_a)

# Ora puoi importare
from model.product_model import ProductModel
from presentation.controller.guest_controller import ControllerGuest
from model.prodotto_finito_cliente import ProdottoFinito


class StoriaProdottoView(QWidget):
    def __init__(self, prodotto : ProductModel, parent=None):
        super().__init__(parent)
        self.prodotto : ProductModel = prodotto
        self.guest_controller = ControllerGuest()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setGeometry(0, 0, 750, 650)

        titolo = QLabel(f"<h3>Storia del Prodotto: {self.prodotto.Nome_prodotto} (ID: {self.prodotto.Id_prodotto})</h3>")
        layout.addWidget(titolo)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Descrizione"])

        self.mostra_storia(self.prodotto, self.tree.invisibleRootItem())

        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.setWindowTitle("Storia del Prodotto")

    def mostra_storia(self, prodotto : ProductModel, parent_item):
        item_prodotto = QTreeWidgetItem([f"Prodotto: {prodotto.Nome_prodotto} (ID: {prodotto.Id_prodotto})"])
        parent_item.addChild(item_prodotto)

        for componente in prodotto.componenti:
            for trasformazione in componente.trasformazioni:
                item_trasf = QTreeWidgetItem([f"↳ Trasformazione: {trasformazione.Nome_operazione} ({trasformazione.Nome_azienda})"])
                item_prodotto.addChild(item_trasf)

            sotto_prodotto = self.guest_controller.carica_prodotto_con_storia(componente.prodotto_id)
            self.mostra_storia(sotto_prodotto, item_prodotto)
