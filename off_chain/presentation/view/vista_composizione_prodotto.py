from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QListWidget, QListWidgetItem,
    QPushButton, QInputDialog, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal

from model.product_model import ProductModel  
from presentation.controller.company_controller import ControllerAzienda
from model.materia_prima_model import MateriaPrimaModel 


class VistaCreaProdottoTrasformato(QDialog):

    operazione_aggiunta = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Crea Nuovo Prodotto Trasformato")
        self.controller = ControllerAzienda()
        
        self.materie_prime : list[MateriaPrimaModel] = self.controller.get_materie_prime_magazzino_azienda()  


        self.quantita_usata_per_materia = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nome prodotto:"))
        self.input_nome = QLineEdit()
        layout.addWidget(self.input_nome)

        layout.addWidget(QLabel("Quantità prodotta:"))
        self.input_quantita = QSpinBox()
        self.input_quantita.setMinimum(1)
        layout.addWidget(self.input_quantita)

        layout.addWidget(QLabel("Seleziona materie prime da utilizzare:"))
        self.lista_materie = QListWidget()
        for mp in self.materie_prime:
            item = QListWidgetItem(f"{mp.nome} - Disponibile: {mp.quantita}")  
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, mp)  # ✅ Salva l'intero oggetto
            self.lista_materie.addItem(item)
        layout.addWidget(self.lista_materie)

        self.btn_quantita_usata = QPushButton("Specifica quantità usata per le materie selezionate")
        self.btn_quantita_usata.clicked.connect(self.specifica_quantita_usata)
        layout.addWidget(self.btn_quantita_usata)

        self.btn_salva = QPushButton("Crea Prodotto")
        self.btn_salva.clicked.connect(self.crea_prodotto)
        layout.addWidget(self.btn_salva)

        self.setLayout(layout)

    def specifica_quantita_usata(self):
        self.quantita_usata_per_materia.clear()
        for i in range(self.lista_materie.count()):
            item = self.lista_materie.item(i)
            if item.checkState() == Qt.Checked:
                materia: MateriaPrimaModel = item.data(Qt.UserRole)
                if isinstance(materia, MateriaPrimaModel):
                    q, ok = QInputDialog.getInt(
                        self,
                        "Quantità usata",
                        f"Quanta quantità usare di {materia.nome}?",
                        min=1,
                        max= materia.quantita,  # Placeholder per la quantità disponibile
                    )
                    if ok:
                        self.quantita_usata_per_materia[materia.id_prodotto] = (materia, q)

    def crea_prodotto(self):
        nome = self.input_nome.text().strip()
        quantita = self.input_quantita.value()

        if not nome:
            QMessageBox.warning(self, "Errore", "Inserisci il nome del nuovo prodotto.")
            return

        if not self.quantita_usata_per_materia:
            QMessageBox.warning(self, "Errore", "Specifica le quantità delle materie prime selezionate.")
            return

        for _, (materia , q) in self.quantita_usata_per_materia.items():
            if isinstance(materia, MateriaPrimaModel):
                if q <= 0:
                    QMessageBox.warning(self, "Errore", f"La quantità usata deve essere maggiore di zero per {materia.nome}.")
                    return
                if q > materia.quantita:
                    QMessageBox.warning(self, "Errore", f"La quantità usata supera la disponibilità di {materia.nome}.")
                    return

        co2, ok = QInputDialog.getInt(
            self,
            "Consumo CO₂",
            "Inserisci il consumo di CO₂ (in kg):",
            decimals=0,
            min=0
        )
        if not ok:
            QMessageBox.information(self, "Annullato", "Creazione del prodotto annullata.")
            return

        self.controller.crea_prodotto_trasformato(nome, quantita, self.quantita_usata_per_materia, co2)

        QMessageBox.information(self, "Salvato", "Prodotto trasformato creato con successo!")
        self.operazione_aggiunta.emit()
        self.accept()



