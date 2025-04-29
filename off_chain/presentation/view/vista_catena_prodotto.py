from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget, QLineEdit, QLabel
)
import sys
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl

class LottoTreeView(QMainWindow):
    def __init__(self, lotto_id):
        super().__init__()
        self.setWindowTitle("Catena di Produzione - Lotto")
        self.setGeometry(100, 100, 800, 600)

        self.manager = ProductRepositoryImpl()
        self.lotto_id = lotto_id

        # Campo di testo per il consumo unitario
        self.co2_unit_field = QLineEdit()
        self.co2_unit_field.setReadOnly(True)
        self.co2_unit_field.setPlaceholderText("Consumo unitario CO₂ (kg/unità)")

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ID Lotto", "Tipo", "Quantità", "CO₂ (kg)", "Quantità utilizzata"])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Consumo unitario CO₂:"))
        layout.addWidget(self.co2_unit_field)
        layout.addWidget(self.tree)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.carica_albero_lotti(self.lotto_id, self.tree.invisibleRootItem())
        self.aggiorna_campo_consumo_unitario()

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
            str(quantita_usata),
        ])
        parent_item.addChild(item)

        for comp in lotto.composizione:
            self.carica_albero_lotti(comp.id_lotto_input, item, comp.quantita_utilizzata)

    def aggiorna_campo_consumo_unitario(self):
        lotto = self.manager.carica_lotto_con_composizione(self.lotto_id)
        if lotto:
            try:
                # Metodo ipotetico del modello `lotto` per ottenere il consumo unitario
                consumo_unitario = lotto.get_costo_totale_lotto_unitario()
                self.co2_unit_field.setText(f"{consumo_unitario:.4f} kg/unità")
            except Exception as e:
                self.co2_unit_field.setText("Errore nel calcolo")
        else:
            self.co2_unit_field.setText("Lotto non trovato")
