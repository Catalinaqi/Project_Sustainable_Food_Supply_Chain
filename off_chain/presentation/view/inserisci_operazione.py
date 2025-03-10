from PyQt5.QtCore import Qt, QRegExp, QDate
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QFormLayout, QLineEdit,
                             QHBoxLayout, QPushButton, QComboBox, QMessageBox, QDateEdit, QDialog, QTextEdit)

from off_chain.presentation.controller.company_controller import ControllerAzienda
from off_chain.presentation.view import funzioni_utili


def operazioni(tipo):
    if tipo == "Agricola":
        return ["Produzione"]
    if tipo == "Trasportatore":
        return ["Trasporto"]
    if tipo == "Trasformatore":
        return ["Trasformazione", "Produzione"]
    if tipo == "Rivenditore":
        return ["Messo sugli scaffali"]


class VistaInserisciOperazione(QMainWindow):
    def __init__(self, callback, azienda):
        super().__init__()

        self.controller = ControllerAzienda()

        self.callback = callback
        self.azienda = azienda
        self.tipo_azienda = self.azienda[2]

        # Elementi di layout
        self.azienda_label = QLabel("Azienda")
        self.azienda_input = QLineEdit(self.azienda[3])
        self.prodotto_label = QLabel('Prodotto')
        self.prodotto_input = QComboBox()
        self.quantita_label = QLabel('Quantità')
        self.quantita_input = QLineEdit()
        self.destinazione_label = QLabel('Destinazione')
        self.destinazione_input = QComboBox()
        self.operazione_label = QLabel('Operazione')
        self.operazione_input = QComboBox()
        self.co2_label = QLabel('CO2 consumata')
        self.co2_input = QLineEdit()
        self.data_label = QLabel('Data')
        self.data_input = QDateEdit()
        self.conferma_button = QPushButton('Conferma')

        self.setWindowIcon(QIcon("presentation\\resources\\logo_centro.png"))

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)  # Centra verticalmente

        welcome_label = QLabel('Completa i seguenti campi')
        funzioni_utili.insert_label(welcome_label, main_layout)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        form_container = QVBoxLayout()
        form_container.addLayout(form_layout)
        form_container.setContentsMargins(150, 0, 150, 0)

        self.azienda_input.setReadOnly(True)
        funzioni_utili.add_field_to_form(self.azienda_label, self.azienda_input, form_layout)

        if self.tipo_azienda == "Agricola" or self.tipo_azienda == "Trasformatore":
            funzioni_utili.add_field_to_form(self.quantita_label, self.quantita_input, form_layout)
            if self.tipo_azienda == "Trasformatore":
                self.quantita_label.setVisible(False)
                self.quantita_input.setVisible(False)

        self.destinazione_input.addItems(["Azienda di trasformazione", "Rivenditore finale"])
        if self.tipo_azienda == "Trasportatore":
            funzioni_utili.add_field_to_form(self.destinazione_label, self.destinazione_input, form_layout)

        self.operazione_input.addItems(operazioni(self.tipo_azienda))
        funzioni_utili.add_field_to_form(self.operazione_label, self.operazione_input, form_layout)
        if self.tipo_azienda == "Trasformatore":
            self.operazione_input.currentIndexChanged.connect(self.update_prodotti_combobox_trasformatore)
        if self.tipo_azienda == "Trasportatore":
            self.destinazione_input.currentIndexChanged.connect(self.update_prodotti_combobox_trasportatore)

        opzioni = self.controller.elementi_combo_box(
            self.tipo_azienda, self.operazione_input.currentText(), self.destinazione_input.currentText())
        if (self.tipo_azienda != "Agricola" or
                (self.tipo_azienda == "Trasformazione" and self.operazione_input.currentText() == "Trasformazione")):
            opzioni = [f"ID: {t[0]}, Nome: {t[1]}, Quantità: {t[2]}" for t in opzioni]
        self.prodotto_input.addItems(opzioni)
        funzioni_utili.add_field_to_form(self.prodotto_label, self.prodotto_input, form_layout)

        self.co2_input.setValidator(QRegExpValidator(QRegExp(r"^\d+(\.\d{1,})?$")))
        funzioni_utili.add_field_to_form(self.co2_label, self.co2_input, form_layout)

        self.data_input.setCalendarPopup(True)
        self.data_input.setDisplayFormat("dd/MM/yyyy")
        self.data_input.setDate(QDate.currentDate())
        funzioni_utili.add_field_to_form(self.data_label, self.data_input, form_layout)

        main_layout.addLayout(form_container)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        funzioni_utili.insert_button(self.conferma_button, button_layout)
        self.conferma_button.clicked.connect(self.on_conferma_button_clicked)

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def update_prodotti_combobox_trasformatore(self):
        self.prodotto_input.setStyleSheet(
            "border-radius: 10px; border: 2px solid green; color: black; padding: 5px"
        )

        if self.quantita_input.isVisible():
            self.quantita_label.setVisible(False)
            self.quantita_input.setVisible(False)
        else:
            self.quantita_label.setVisible(True)
            self.quantita_input.setVisible(True)

        operazione_selezionata = self.operazione_input.currentText()

        opzioni_prodotti = self.controller.elementi_combo_box(self.tipo_azienda, operazione_selezionata)
        if operazione_selezionata == "Trasformazione":
            opzioni_prodotti = [f"ID: {t[0]}, Nome: {t[1]}, Quantità: {t[2]}" for t in opzioni_prodotti]

        self.prodotto_input.clear()  # Pulisci la lista precedente
        self.prodotto_input.addItems(opzioni_prodotti)  # Aggiungi i nuovi prodotti

    def update_prodotti_combobox_trasportatore(self):
        self.prodotto_input.setStyleSheet(
            "border-radius: 10px; border: 2px solid green; color: black; padding: 5px"
        )

        destinazione_selezionata = self.destinazione_input.currentText()
        operazione_selezionata = self.operazione_input.currentText()

        opzioni_prodotti = self.controller.elementi_combo_box(
            self.tipo_azienda, operazione_selezionata, destinazione_selezionata
        )
        opzioni_prodotti = [f"ID: {t[0]}, Nome: {t[1]}, Quantità: {t[2]}" for t in opzioni_prodotti]

        self.prodotto_input.clear()  # Pulisci la lista precedente
        self.prodotto_input.addItems(opzioni_prodotti)  # Aggiungi i nuovi prodotti

    def on_conferma_button_clicked(self):
        global prodotto
        quantita = ''
        nuovo_stato = 0
        azienda = self.azienda[0]
        data = self.data_input.text()
        co2 = self.co2_input.text()
        operazione = self.operazione_input.currentText()
        prodotto_index = self.prodotto_input.currentIndex()
        destinazione = self.destinazione_input.currentText()

        non_vuoti = [co2]

        if prodotto_index == -1:
            QMessageBox.warning(self, "SupplyChain",
                                "Non ci sono prodotti con cui effettuare operazioni!")
            self.prodotto_input.setStyleSheet(
                "border-radius: 10px; border: 2px solid red; color: black; padding: 5px"
            )
        else:
            prodotto = self.controller.elementi_combo_box(
                self.tipo_azienda, operazione, destinazione
            )[prodotto_index]

            if self.tipo_azienda == "Agricola" or self.tipo_azienda == "Trasformatore":
                quantita = self.quantita_input.text()
                if self.operazione_input.currentText() == "Produzione":
                    non_vuoti.append(quantita)

            if self.tipo_azienda == "Trasportatore":
                destinazione = self.destinazione_input.currentText()
                if destinazione == "Azienda di trasformazione":
                    nuovo_stato = 0o1
                elif destinazione == "Rivenditore finale":
                    nuovo_stato = 11
                else:
                    pass

            if funzioni_utili.is_blank(non_vuoti):
                QMessageBox.warning(self, "SupplyChain", "Completare tutti i campi!")
            else:
                self.aggiungi(azienda, prodotto, quantita, operazione, co2, data, nuovo_stato)

    def aggiungi(self, azienda, prodotto, quantita, operazione, co2, data, nuovo_stato):
        evento = ("", "")
        if self.tipo_azienda == "Agricola":
            self.controller.aggiungi_operazione(
                self.tipo_azienda, azienda, prodotto, data, co2, operazione, quantita=quantita
            )
            evento = (operazione, prodotto)

        elif self.tipo_azienda == "Trasportatore":
            self.controller.aggiungi_operazione(
                self.tipo_azienda, azienda, prodotto[0], data, co2, operazione, nuovo_stato=nuovo_stato
            )
            evento = (operazione, prodotto[1])
        elif self.tipo_azienda == "Trasformatore":
            if operazione == "Trasformazione":
                self.controller.aggiungi_operazione(
                    self.tipo_azienda, azienda, prodotto, data, co2, operazione, quantita=quantita
                )
                evento = (operazione, prodotto[1])
            else:
                opzioni = self.controller.get_prodotti_to_composizione(self.azienda[0])
                dialog = ComposizioneDialog(opzioni)
                if dialog.exec_():  # Se l'utente conferma
                    prodotti_composizione = dialog.get_composizione()
                    if not prodotti_composizione:
                        QMessageBox.warning(self, "SupplyChain",
                                            "Impossibile procedere!\n"
                                            "Bisogna aggiungere dei prodotti per la "
                                            "composizione!")
                        return  # Se la composizione è vuota, esce senza chiudere la view

                    self.controller.aggiungi_operazione(
                        self.tipo_azienda, azienda, prodotto, data, co2, operazione,
                        quantita=quantita, materie_prime=prodotti_composizione
                    )
                    evento = (operazione, prodotto)
                else:
                    return  # Se il dialog viene chiuso senza confermare, esce senza chiudere la view

        elif self.tipo_azienda == "Rivenditore":
            self.controller.aggiungi_operazione(
                self.tipo_azienda, azienda, prodotto[0], data, co2, operazione
            )
            evento = (operazione, prodotto[1])
        scarto = self.controller.scarto_soglia(co2, evento[0], evento[1])
        QMessageBox.information(self, "SupplyChain", f"Operazione inserita correttamente!\n"
                                                     f"Scarto CO2 consumata rispetto alla soglia massima: "
                                                     f"{scarto}")
        self.callback()
        self.close()


class ComposizioneDialog(QDialog):
    def __init__(self, prodotti_disponibili, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Composizione Prodotti")

        testi_to_combo_box = [f"ID: {t[0]}, Nome: {t[1]}, Quantità: {t[2]}"
                              for t in prodotti_disponibili]
        self.prodotti_from_controller = prodotti_disponibili

        # Copia della lista per evitare modifiche esterne
        self.prodotti_disponibili = testi_to_combo_box[:]
        self.prodotti_selezionati = []

        self.prodotti_to_controller = []

        # Layout principale
        layout = QVBoxLayout(self)

        # Label sopra la combobox
        self.label_selezione = QLabel("Seleziona i prodotti per la composizione")
        layout.addWidget(self.label_selezione)

        # Combobox per selezionare i prodotti
        self.combo_prodotti = QComboBox()
        self.combo_prodotti.addItems(self.prodotti_disponibili)
        layout.addWidget(self.combo_prodotti)

        # Pulsante "Aggiungi"
        self.btn_aggiungi = QPushButton("Aggiungi")
        layout.addWidget(self.btn_aggiungi)

        # Testo che mostra i prodotti selezionati
        self.label_selezionati = QLabel("Prodotti selezionati:")
        layout.addWidget(self.label_selezionati)

        self.text_selezionati = QTextEdit()
        self.text_selezionati.setReadOnly(True)
        layout.addWidget(self.text_selezionati)

        # Pulsanti "Conferma Composizione" e "Annulla"
        btn_layout = QHBoxLayout()
        self.btn_conferma = QPushButton("Conferma Composizione")
        self.btn_annulla = QPushButton("Annulla")
        btn_layout.addWidget(self.btn_conferma)
        btn_layout.addWidget(self.btn_annulla)
        layout.addLayout(btn_layout)

        # Connessioni dei pulsanti
        self.btn_aggiungi.clicked.connect(self.aggiungi_prodotto)
        self.btn_annulla.clicked.connect(self.reject)  # Chiude il dialogo senza confermare
        self.btn_conferma.clicked.connect(self.accept)  # Conferma la composizione

        # Disabilita "Aggiungi" se non ci sono prodotti disponibili
        self.aggiorna_stato_bottoni()

    def aggiungi_prodotto(self):
        """Aggiunge il prodotto selezionato alla lista, lo rimuove dalla combobox e aggiorna il testo."""
        prodotto = self.combo_prodotti.currentText()
        index = self.combo_prodotti.currentIndex()
        if prodotto:
            self.prodotti_selezionati.append(prodotto)
            self.text_selezionati.setPlainText("\n".join(self.prodotti_selezionati))
            self.prodotti_to_controller.append(
                self.prodotti_from_controller[index][0]
            )

    def aggiorna_stato_bottoni(self):
        """Disabilita il pulsante Aggiungi se non ci sono più prodotti da selezionare."""
        self.btn_aggiungi.setEnabled(self.combo_prodotti.count() > 0)

    def get_composizione(self):
        """Restituisce la lista dei prodotti selezionati."""
        return list(sorted(set(self.prodotti_to_controller)))
