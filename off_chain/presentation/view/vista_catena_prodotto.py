from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
import sys
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl

class LottoTreeView(QMainWindow):
    def __init__(self, lotto_id):
        super().__init__()
        self.setWindowTitle("Catena di Produzione - Lotto")
        self.setGeometry(100, 100, 800, 600)

        self.manager = ProductRepositoryImpl()
        self.lotto_id = lotto_id

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ID Lotto", "Tipo", "Quantità", "CO₂ (kg)", "Quantità utilizzata"])

        layout = QVBoxLayout()
        layout.addWidget(self.tree)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.carica_albero_lotti(self.lotto_id, self.tree.invisibleRootItem())

    def carica_albero_lotti(self, id_lotto, parent_item, quantita_usata=""):
        lotto = self.manager.carica_lotto_con_composizione(id_lotto)
        if not lotto:
            item = QTreeWidgetItem(["[Lotto non trovato]", "", "", "", ""])
            parent_item.addChild(item)
            return

        item = QTreeWidgetItem([
            str(lotto.id_lotto),
            str(lotto.tipo),
            str(lotto.quantita),
            str(lotto.cons_co2),
            str(quantita_usata)
        ])
        parent_item.addChild(item)

        for comp in lotto.composizione:
            self.carica_albero_lotti(comp.id_lotto_input, item, comp.quantita_utilizzata)

