from datetime import date

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout, QPushButton, QMenu, \
    QMessageBox, QInputDialog, QDialog, QComboBox, QDialogButtonBox, QLineEdit, QCompleter

from presentation.view import funzioni_utili
from presentation.view.vista_operazioni import VistaOperazioni


class VistaProdotti(QMainWindow):
    def __init__(self, controller, certificatore=None, filtro_certificazioni=False):
        super().__init__()

        # self.callback = callback
        self.controller = controller
        self.certificatore = certificatore
        self.filtro_certificazioni = filtro_certificazioni

        self.ordinata = False
        self.nome_filtro = ''
        self.rivenditore_filtro = 0

        # Elementi di layout
        self.list_view = QListView()
        self.info_button = QPushButton("Visualizza informazioni prodotto")
        self.certifica_button = QPushButton("Assegna certificazione")
        self.button_filtro = QPushButton("Filtri")

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

        label = QLabel("Lista Prodotti")
        if self.filtro_certificazioni:
            label.setText("Lista prodotti certificati")

        funzioni_utili.insert_label(label, main_layout)

        funzioni_utili.insert_list(self.list_view, main_layout)
        self.genera_lista()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)  # Centra orizzontalmente

        funzioni_utili.insert_button(self.info_button, button_layout)

        if self.certificatore:
            funzioni_utili.insert_button(self.certifica_button, button_layout)
            self.certifica_button.clicked.connect(self.on_certifica_button_clicked)

        funzioni_utili.insert_button(self.button_filtro, button_layout)

        menu_info = QMenu()
        funzioni_utili.config_menu(
            menu_info,
            [
                ("Visualizza info prodotto", self.info),
                ("Visualizza storico", lambda: self.info('storico')),
                ("Visualizza certificazione", lambda: self.info('certificato')),
            ],
            self.info_button
        )

        menu_filtri = QMenu()
        funzioni_utili.config_menu(
            menu_filtri,
            [
                ("Cerca per nome", self.on_button_filtro_nome_clicked),
                ("Cerca per rivenditore", self.on_button_filtro_rivenditore_clicked),
                ("Ordina per co2 consumata", self.on_button_ordina_clicked),
                ("Resetta filtro", self.on_button_reset_clicked),
            ],
            self.button_filtro
        )

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def lista_giusta(self, filtro_certificazioni, nome=None, rivenditore=None, ordinata=None):
        if not filtro_certificazioni:
            if not nome and not rivenditore and not ordinata:
                return self.controller.lista_prodotti()
            elif nome:
                return self.controller.prodotti_by_nome(nome)
            elif rivenditore:
                return self.controller.lista_prodotti_rivenditore(rivenditore)
            elif ordinata:
                return self.controller.lista_prodotti_ordinati_co2()
        else:
            if not nome and not rivenditore and not ordinata:
                return self.controller.lista_prodotti_certificati()
            elif nome:
                return self.controller.lista_prodotti_certificati_by_nome(nome)
            elif rivenditore:
                return self.controller.lista_prodotti_certificati_rivenditore(rivenditore)
            elif ordinata:
                return self.controller.lista_prodotti_certificati_ordinata()

    def genera_lista(self):
        self.nome_filtro = ''
        self.rivenditore_filtro = 0
        self.ordinata = False
        model = QStandardItemModel()
        for f in self.lista_giusta(self.filtro_certificazioni):
            item = QStandardItem(f"ID: {f[0][0]}\n"
                                 f"Nome: {f[0][1]}\n"
                                 f"Rivenditore: {f[0][4]}\n"
                                 f"CO2 consumata per la produzione: {f[1]}")
            if self.controller.is_certificato(f[0][0]):
                item.setText(f"ID: {f[0][0]} ★\n"
                             f"Nome: {f[0][1]}\n"
                             f"Rivenditore: {f[0][4]}\n"
                             f"CO2 consumata per la produzione: {f[1]}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def genera_lista_filtrata_nome(self, nome):
        lista_by_nome = self.lista_giusta(
            self.filtro_certificazioni, nome=nome
        )
        if len(lista_by_nome) == 0:
            QMessageBox.information(
                self, 'SupplyChain', f'Non ci sono prodotti con il seguente nome: {nome}')
            self.genera_lista()
        else:
            model = QStandardItemModel()
            for f in lista_by_nome:
                item = QStandardItem(f"ID: {f[0][0]}\n"
                                     f"Nome: {f[0][1]}\n"
                                     f"Rivenditore: {f[0][4]}\n"
                                     f"CO2 consumata per la produzione: {f[1]}")
                if self.controller.is_certificato(f[0][0]):
                    item.setText(f"ID: {f[0][0]} ★\n"
                                 f"Nome: {f[0][1]}\n"
                                 f"Rivenditore: {f[0][4]}\n"
                                 f"CO2 consumata per la produzione: {f[1]}")
                item.setEditable(False)
                item.setFont(QFont("Times Roman", 11))
                model.appendRow(item)
            self.list_view.setModel(model)

    def genera_lista_filtrata_rivenditore(self, r):
        lista_by_rivenditore = self.lista_giusta(
            self.filtro_certificazioni, rivenditore=r
        )
        if len(lista_by_rivenditore) == 0:
            QMessageBox.information(
                self, 'SupplyChain', f'Non ci sono prodotti con il seguente rivenditore: {r}')
            self.genera_lista()
        else:
            model = QStandardItemModel()
            for f in lista_by_rivenditore:
                item = QStandardItem(f"ID: {f[0][0]}\n"
                                     f"Nome: {f[0][1]}\n"
                                     f"Rivenditore: {f[0][4]}\n"
                                     f"CO2 consumata per la produzione: {f[1]}")
                if self.controller.is_certificato(f[0][0]):
                    item.setText(f"ID: {f[0][0]} ★\n"
                                 f"Nome: {f[0][1]}\n"
                                 f"Rivenditore: {f[0][4]}\n"
                                 f"CO2 consumata per la produzione: {f[1]}")
                item.setEditable(False)
                item.setFont(QFont("Times Roman", 11))
                model.appendRow(item)
            self.list_view.setModel(model)

    def on_button_ordina_clicked(self):
        self.ordinata = True
        self.nome_filtro = ''
        self.rivenditore_filtro = 0
        lista_ordinata = self.lista_giusta(
            self.filtro_certificazioni, ordinata=True
        )
        model = QStandardItemModel()
        for f in lista_ordinata:
            item = QStandardItem(f"ID: {f[0][0]}\n"
                                 f"Nome: {f[0][1]}\n"
                                 f"Rivenditore: {f[0][4]}\n"
                                 f"CO2 consumata per la produzione: {f[1]}")
            if self.controller.is_certificato(f[0][0]):
                item.setText(f"ID: {f[0][0]} ★\n"
                             f"Nome: {f[0][1]}\n"
                             f"Rivenditore: {f[0][4]}\n"
                             f"CO2 consumata per la produzione: {f[1]}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def on_button_filtro_rivenditore_clicked(self):
        # Crea un QDialog personalizzato
        dialog = QDialog(self)
        dialog.setWindowTitle("SupplyChain")

        layout = QVBoxLayout(dialog)

        # Crea una QComboBox e aggiungi le opzioni
        combo = QComboBox(dialog)
        rivenditori = [t[3] for t in self.controller.lista_rivenditori()]
        options = rivenditori
        combo.addItems(options)
        layout.addWidget(combo)

        # Aggiungi i pulsanti "Ok" e "Cancel"
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(buttons)

        # Definisci cosa succede quando l'utente clicca su "Ok"
        def on_accept():
            selected_option = combo.currentText()
            if selected_option.strip() == "":
                QMessageBox.warning(dialog, 'Errore', 'Devi selezionare qualcosa!')
            else:
                index = combo.currentIndex()
                self.rivenditore_filtro = self.controller.lista_rivenditori()[index][0]
                self.nome_filtro = ''
                self.ordinata = False
                self.genera_lista_filtrata_rivenditore(self.rivenditore_filtro)
                dialog.accept()

        # Collega i pulsanti alle funzioni
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        # Mostra il dialogo
        dialog.exec_()

    def on_button_filtro_nome_clicked(self):
        # Crea un QDialog personalizzato
        dialog = QDialog(self)
        dialog.setWindowTitle("SupplyChain")

        layout = QVBoxLayout(dialog)

        label = QLabel("Inserisci il nome del prodotto:")
        layout.addWidget(label)

        # Crea una QComboBox e aggiungi le opzioni
        line_edit = QLineEdit(dialog)
        options = [prodotto[0][1] for prodotto in self.controller.lista_prodotti()]
        completer = QCompleter(options)
        completer.setCaseSensitivity(False)
        completer.setFilterMode(Qt.MatchContains)
        line_edit.setCompleter(completer)
        layout.addWidget(line_edit)

        # Aggiungi i pulsanti "Ok" e "Cancel"
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(buttons)

        # Definisci cosa succede quando l'utente clicca su "Ok"
        def on_accept():
            selected_option = line_edit.text()
            if selected_option.strip() == "":
                QMessageBox.warning(dialog, 'Errore', 'Devi selezionare qualcosa!')
            else:
                self.nome_filtro = selected_option.strip()
                self.rivenditore_filtro = 0
                self.ordinata = False
                self.genera_lista_filtrata_nome(self.nome_filtro)
                dialog.accept()

        # Collega i pulsanti alle funzioni
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        # Mostra il dialogo
        dialog.exec_()

    def on_button_reset_clicked(self):
        self.genera_lista()

    def on_certifica_button_clicked(self):
        self.info('certifica')

    def info(self, info=''):
        global prodotto
        selected_index = self.list_view.selectedIndexes()

        if selected_index:
            selected_item = selected_index[0].row()  # Ottieni l'indice dell'elemento selezionato
            if not self.ordinata and self.nome_filtro == '' and self.rivenditore_filtro == 0:
                prodotto = self.lista_giusta(
                    self.filtro_certificazioni
                )[selected_item]
            else:
                if not self.ordinata:
                    if self.nome_filtro == '':
                        prodotto = self.lista_giusta(
                            self.filtro_certificazioni,
                            rivenditore=self.rivenditore_filtro
                        )[
                            selected_item
                        ]
                    elif self.rivenditore_filtro == 0:
                        prodotto = self.lista_giusta(
                            self.filtro_certificazioni,
                            nome=self.nome_filtro
                        )[
                            selected_item
                        ]
                else:
                    prodotto = self.lista_giusta(
                        self.filtro_certificazioni, ordinata=True
                    )[selected_item]

            if info == '':
                QMessageBox.information(self, "SupplyChain",
                                        f"Prodotto selezionato:\n"
                                        f"ID: {prodotto[0][0]}\n"
                                        f"Nome: {prodotto[0][1]}\n"
                                        f"Quantità: {prodotto[0][2]}\n"
                                        f"Rivenditore: {prodotto[0][4]}\n"
                                        f"CO2 consumata: {prodotto[1]}")
            elif info == 'certificato':
                id_prodotto_selezionato = prodotto[0][0]
                certificati_filtrati = self.controller.certificazione_by_prodotto(id_prodotto_selezionato)

                if certificati_filtrati:
                    certificato = certificati_filtrati[0]
                    testo = (f"ID: {certificato[0]}\n"
                             f"Nome prodotto: {certificato[1]}\n"
                             f"Tipo: {certificato[2]}\n"
                             f"Azienda: {certificato[3]}\n"
                             f"Data: {certificato[4]}")
                    QMessageBox.information(self, "Certificato", testo)
                else:
                    QMessageBox.information(self, "Certificato non trovato",
                                            "Nessun certificato disponibile per questo prodotto.")
            elif info == 'storico':
                self.storico_view = VistaOperazioni(self.controller, is_storico=True, prodotto=prodotto)
                self.storico_view.show()

            elif info == 'certifica':
                id_prodotto_selezionato = prodotto[0][0]
                certificati_filtrati = self.controller.certificazione_by_prodotto(id_prodotto_selezionato)

                if certificati_filtrati:
                    QMessageBox.information(self, "Certificato", "Prodotto già certificato!")
                else:
                    while True:
                        text, ok = QInputDialog.getText(self, 'SupplyChain', 'Tipo certificazione:')

                        if not ok:
                            break

                        if text.strip() == '':
                            QMessageBox.warning(self, 'Errore', 'Devi digitare qualcosa!')
                            continue

                        else:

                            self.controller.inserisci_certificato(
                                id_prodotto_selezionato, text.strip(), self.certificatore[0], date.today()
                            )
                            QMessageBox.information(self, "SupplyChain",
                                                    f"Certificazione creata!\n"
                                                    f"ID Prodotto: {prodotto[0][0]}\n"
                                                    f"Nome Prodotto: {prodotto[0][1]}\n"
                                                    f"Tipo: {text}\n"
                                                    f"Azienda: {self.certificatore[3]}\n"
                                                    f"Data: {date.today().strftime('%d/%m/%Y')}")
                            self.genera_lista()
                            break
        else:
            QMessageBox.warning(self, "Nessuna selezione", "Nessun item è stato selezionato.")
