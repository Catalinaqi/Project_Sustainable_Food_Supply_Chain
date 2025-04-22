from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt

from model.product_model import ProductModel

class VistaInviaRichiesta(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invia Richiesta")

        #self.prodotti = controller_prodotti.get_lista_prodotti()
        self.prodotti = [
            ProductModel(1, "Prodotto A", []),
            ProductModel(2, "Prodotto B", []),
            ProductModel(3, "Prodotto C", []),
        ]

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Seleziona un prodotto disponibile:"))

        self.lista_prodotti = QListWidget()
        for prodotto in self.prodotti:
            item = QListWidgetItem(
                f"{prodotto.Nome_prodotto} - {prodotto.Id_prodotto} - CO2: {10} - Disponibilità: {100}"
            )
            item.setData(Qt.UserRole, prodotto)
            self.lista_prodotti.addItem(item)
        layout.addWidget(self.lista_prodotti)

        # Quantità richiesta
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Quantità da richiedere:"))
        self.input_quantita = QLineEdit()
        form_layout.addWidget(self.input_quantita)
        layout.addLayout(form_layout)

        # Bottone per inviare la richiesta
        self.bottone_invia = QPushButton("Invia Richiesta")
        self.bottone_invia.clicked.connect(self.invia_richiesta)
        layout.addWidget(self.bottone_invia)

        self.setLayout(layout)

    def invia_richiesta(self):
        item_selezionato = self.lista_prodotti.currentItem()
        if not item_selezionato:
            QMessageBox.warning(self, "Errore", "Seleziona un prodotto.")
            return

        prodotto : ProductModel = item_selezionato.data(Qt.UserRole)
        try:
            quantita = int(self.input_quantita.text())
        except ValueError:
            QMessageBox.warning(self, "Errore", "Inserisci una quantità valida.")
            return

        if quantita <= 0 or quantita > 100:  # Placeholder per la quantità disponibile
            QMessageBox.warning(
                self,
                "Errore",
                f"La quantità deve essere positiva e non superiore alla disponibilità."
            )
            return

        # Invia la richiesta tramite callback
        print(f"Richiesta inviata per {prodotto.Nome_prodotto} - Quantità: {quantita}")
        QMessageBox.information(self, "Successo", "Richiesta inviata con successo!")
        self.close()

