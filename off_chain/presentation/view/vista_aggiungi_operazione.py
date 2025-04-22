from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QDateEdit, QLineEdit, QComboBox, QDoubleSpinBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import pyqtSignal, Qt

from model.operation_model import OperationModel
from model.product_model import ProductModel
from session import Session
from presentation.controller.company_controller import PERMESSI_OPERAZIONI, ControllerAzienda
from PyQt5.QtWidgets import QComboBox , QMessageBox, QDoubleSpinBox , QListWidget, QListWidgetItem, QLabel, QVBoxLayout



class AggiungiOperazioneView(QDialog):
    operazione_aggiunta = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ControllerAzienda()
        self.role_azienda : str = Session().current_user["role"]
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Aggiungi Operazione")

        layout = QVBoxLayout()

        

        layout.addWidget(QLabel("Tipo operazione:"))
        self.input_tipo = QComboBox()
        permessi = PERMESSI_OPERAZIONI.get(self.role_azienda, [])
        self.input_tipo.addItems(permessi)
        layout.addWidget(self.input_tipo)


        self.input_testo = QLineEdit()
        self.input_testo.setMaxLength(25)


        self.input_ricerca_prodotto = QLineEdit()
        self.lista_prodotti = QListWidget()
        self.lista_prodotti.setSelectionMode(QListWidget.NoSelection)  

        if self.role_azienda == "Agricola" :
            
            # Se il ruolo è Trasformatore o Agricola, mostra il campo di testo per il nome del nuovo prodotto
            self.input_testo.setPlaceholderText("Nome nuovo prodotto")
            layout.addWidget(QLabel("Nome nuovo prodotto:"))
            layout.addWidget(self.input_testo)

            self.input_quantita = QDoubleSpinBox()
            self.input_quantita.setMinimum(0.0)            
            self.input_quantita.setMaximum(10000.0)       
            self.input_quantita.setDecimals(0)          
            self.input_quantita.setSingleStep(1)                    
            layout.addWidget(QLabel("Inserisci quantità prodotta:"))
            layout.addWidget(self.input_quantita)






        

        if  self.role_azienda == "Trasportatore" or self.role_azienda == "Rivenditore":

            # Se il ruolo è Trasformatore, Trasportatore o Rivenditore, mostra la lista dei prodotti

            layout.addWidget(QLabel("Seleziona il prodotto:"))

            if self.role_azienda in ["Distributore", "Trasportatore"]:  
                self.abilita_selezione_singola()


            self.input_ricerca_prodotto.setPlaceholderText("Cerca per nome o ID...")
            layout.addWidget(self.input_ricerca_prodotto)

            
            layout.addWidget(self.lista_prodotti)

            self.prodotti_completi: list[ProductModel] = self.controller.get_prodotti_to_composizione(
                id_azienda=Session().current_user["id_azienda"]
            )

            self.popola_lista_prodotti(self.prodotti_completi)

            # Collegamento del filtro
            self.input_ricerca_prodotto.textChanged.connect(self.filtra_lista_prodotti)


            self.input_quantita = QDoubleSpinBox()
            self.input_quantita.setMinimum(0.0)            
            self.input_quantita.setMaximum(10000.0)       
            self.input_quantita.setDecimals(0)          
            self.input_quantita.setSingleStep(1)                    
            layout.addWidget(QLabel("Inserisci quantità prodotto:"))
            layout.addWidget(self.input_quantita)



        layout.addWidget(QLabel("Data:"))
        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        layout.addWidget(self.input_data)

        

        self.input_valore = QDoubleSpinBox()
        self.input_valore.setMinimum(0.0)            
        self.input_valore.setMaximum(9999.99)       
        self.input_valore.setDecimals(2)          
        self.input_valore.setSingleStep(0.1)                    
        layout.addWidget(QLabel("Inserisci un valore CO2:"))
        layout.addWidget(self.input_valore)


        self.btn_salva = QPushButton("Salva operazione")
        self.btn_salva.clicked.connect(self.salva_operazione)
        layout.addWidget(self.btn_salva)

        self.setLayout(layout)

        self.resize(400, 300)
        self.raise_()
        self.activateWindow()


    def salva_operazione(self):
        try:
            tipo = self.input_tipo.currentText()
            data = self.input_data.date().toPyDate()
            co2 = self.input_valore.value()
            id_azienda = Session().current_user["id_azienda"]

            # Controlli di validità base
            if not tipo:
                QMessageBox.warning(self, "Errore", "Tipo operazione mancante.")
                return

            if co2 <= 0:
                QMessageBox.warning(self, "Errore", "Inserisci un valore di CO2 positivo.")
                return

            """ # Raccolta dei dati specifici in base al ruolo
            if self.role_azienda == "Agricola":
                nome_nuovo_prodotto = self.input_testo.text().strip()
                if not nome_nuovo_prodotto:
                    QMessageBox.warning(self, "Errore", "Devi inserire il nome del nuovo prodotto.")
                    return

                self.controller.salva_operazione_agricola(
                    id_azienda=id_azienda,
                    tipo=tipo,
                    data=data,
                    co2=co2,
                    nome_prodotto=nome_nuovo_prodotto
                )

            elif self.role_azienda == "Trasformatore":
                nome_nuovo_prodotto = self.input_testo.text().strip()
                if not nome_nuovo_prodotto:
                    QMessageBox.warning(self, "Errore", "Devi inserire il nome del nuovo prodotto.")
                    return

                prodotti_selezionati = self.get_prodotti_selezionati()
                if not prodotti_selezionati:
                    QMessageBox.warning(self, "Errore", "Devi selezionare almeno un prodotto.")
                    return

                self.controller.salva_operazione_trasformatore(
                    id_azienda=id_azienda,
                    tipo=tipo,
                    data=data,
                    co2=co2,
                    nome_nuovo_prodotto=nome_nuovo_prodotto,
                    prodotti_usati=prodotti_selezionati
                )

            elif self.role_azienda == "Trasportatore":
                prodotti_selezionati = self.get_prodotti_selezionati()
                if not prodotti_selezionati:
                    QMessageBox.warning(self, "Errore", "Devi selezionare almeno un prodotto.")
                    return

                self.controller.salva_operazione_trasportatore(
                    id_azienda=id_azienda,
                    tipo=tipo,
                    data=data,
                    co2=co2,
                    prodotti_trasportati=prodotti_selezionati
                )

            elif self.role_azienda == "Distributore":
                self.controller.salva_operazione_distributore(
                    id_azienda=id_azienda,
                    tipo=tipo,
                    data=data,
                    co2=co2
                )

            else:
                QMessageBox.critical(self, "Errore", f"Ruolo azienda non gestito: {self.role_azienda}")
                return"""

            # Successo
            self.operazione_aggiunta.emit()
            self.accept()

        except PermissionError as e:
                QMessageBox.critical(self, "Errore di permesso", str(e))
        except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'aggiunta: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {str(e)}")


            


            



    def popola_lista_prodotti(self, prodotti: list[ProductModel]):
        self.lista_prodotti.clear()
        for prodotto in prodotti:
            item = QListWidgetItem(f"{prodotto.Nome_prodotto} (ID: {prodotto.Id_prodotto})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, prodotto)
            self.lista_prodotti.addItem(item)

    def filtra_lista_prodotti(self, testo: str):
        testo = testo.lower().strip()
        prodotti_filtrati = [
            p for p in self.prodotti_completi
            if testo in p.Nome_prodotto.lower() or testo in str(p.Id_prodotto)
        ]
        self.popola_lista_prodotti(prodotti_filtrati)



    def abilita_selezione_singola(self):
        for i in range(self.lista_prodotti.count()):
            item = self.lista_prodotti.item(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        self.lista_prodotti.itemChanged.connect(self.gestisci_selezione_singola)

    def gestisci_selezione_singola(self, item_selezionato: QListWidgetItem):
        if item_selezionato.checkState() == Qt.Checked:
            for i in range(self.lista_prodotti.count()):
                item = self.lista_prodotti.item(i)
                if item != item_selezionato and item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)

    def get_prodotti_selezionati(self) -> list[ProductModel]:
        prodotti = []
        for i in range(self.lista_prodotti.count()):
            item = self.lista_prodotti.item(i)
            if item.checkState() == Qt.Checked:
                prodotto = item.data(Qt.UserRole)
                prodotti.append(prodotto)
        return prodotti



