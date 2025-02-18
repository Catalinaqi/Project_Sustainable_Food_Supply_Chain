from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout, QPushButton, QMenu, \
    QDialog, QComboBox, QDialogButtonBox, QMessageBox, QInputDialog

from off_chain.controllers.controller_guest import ControllerGuest
from off_chain.view import funzioni_utili


class VistaAziende(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.callback = callback
        self.controller = ControllerGuest()

        self.tipo_filtro = ''
        self.nome_filtro = ''
        self.ordinata = False

        self.lista_prova = [
            ((1, "Azienda agricola", "Indirizzo 1", "Azienda agricola La Porta Domenico"), 150, 50),
            ((2, "Azienda di trasporto", "Indirizzo 2", "La Porta Trasporti SRL"), 200, 60),
            ((3, "Azienda di trasformazione", "Indirizzo 3", "Azienda di trasformazione La Porta Tommaso"), 250, 70),
            ((4, "Rivenditore", "Indirizzo 4", "La Standa"), 100, 30),
            ((5, "Azienda agricola", "Indirizzo 5", "Cooperativa Verde"), 120, 40),
            ((6, "Azienda di trasporto", "Indirizzo 6", "Logistica Fast SRL"), 300, 90),
            ((7, "Azienda agricola", "Indirizzo 7", "Fattoria Sole e Mare"), 180, 55),
            ((8, "Rivenditore", "Indirizzo 8", "Mercato Fresco SRL"), 90, 100),
            ((9, "Azienda di trasformazione", "Indirizzo 9", "Trasformazioni Alimentari Rossi"), 275, 80),
            ((10, "Azienda agricola", "Indirizzo 10", "Azienda Agricola Natura SRL"), 140, 45),
            ((11, "Azienda di trasporto", "Indirizzo 11", "Distribuzioni Veloci"), 230, 70),
            ((12, "Rivenditore", "Indirizzo 12", "Supermercati Sempre Freschi"), 110, 35),
            ((13, "Rivenditore", "Indirizzo 13", "Frutta e Verdura Bianchi"), 95, 28),
            ((14, "Azienda agricola", "Indirizzo 14", "Agricoltura Biologica SRL"), 160, 50),
            ((15, "Azienda di trasporto", "Indirizzo 15", "Green Transport Solutions"), 210, 65)
        ]

        # Elementi di layout
        self.list_view = QListView()
        self.info_button = QPushButton("Visualizza informazioni azienda")
        self.button_filtro = QPushButton("Filtri")

        self.setWindowIcon(QIcon("images\\logo_centro.png"))

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

        label = QLabel("Lista Aziende")
        funzioni_utili.insert_label(label, main_layout)

        funzioni_utili.insert_list(self.list_view, main_layout)
        self.genera_lista()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)  # Centra orizzontalmente

        funzioni_utili.insert_button(self.info_button, button_layout)
        self.info_button.clicked.connect(self.info)

        funzioni_utili.insert_button(self.button_filtro, button_layout)

        menu_filtri = QMenu()
        funzioni_utili.config_menu(
            menu_filtri,
            [
                ("Cerca per nome", self.on_button_filtro_nome_clicked),
                ("Cerca per tipo", self.on_button_filtro_tipo_clicked),
                ("Ordina per consumi di CO2", self.on_button_ordina_clicked),
                ("Resetta filtro", self.on_button_reset_clicked),
            ],
            self.button_filtro
        )

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def genera_lista(self):
        self.nome_filtro = ''
        self.tipo_filtro = ''
        self.ordinata = False
        model = QStandardItemModel()
        for f in self.controller.lista_aziende():
            saldo = f[2] - f[1]
            if saldo < 0:
                saldo = f"({-saldo})"
            item = QStandardItem(f"Nome Azienda: {f[0][3]}\nSaldo CO2: {saldo}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def genera_lista_filtrata_tipo(self, tipo):
        lista_by_tipo = self.controller.lista_aziende_filtro_tipo(tipo)
        if len(lista_by_tipo) == 0:
            QMessageBox.information(
                self, 'SupplyChain', f'Non ci sono aziende del seguente tipo: {tipo}')
            self.genera_lista()
        else:
            model = QStandardItemModel()
            for f in lista_by_tipo:
                saldo = f[2] - f[1]
                if saldo < 0:
                    saldo = f"({-saldo})"
                item = QStandardItem(f"Nome Azienda: {f[0][3]}\nSaldo CO2: {saldo}")
                item.setEditable(False)
                item.setFont(QFont("Times Roman", 11))
                model.appendRow(item)
            self.list_view.setModel(model)

    def genera_lista_filtrata_nome(self, nome):
        lista_by_nome = self.controller.azienda_by_nome(nome)
        if len(lista_by_nome) == 0:
            QMessageBox.information(
                self, 'SupplyChain', f'Non ci sono aziende con il seguente nome: {nome}')
            self.genera_lista()
        else:
            model = QStandardItemModel()
            for f in lista_by_nome:
                saldo = f[2] - f[1]
                if saldo < 0:
                    saldo = f"({-saldo})"
                item = QStandardItem(f"Nome Azienda: {f[0][3]}\nSaldo CO2: {saldo}")
                item.setEditable(False)
                item.setFont(QFont("Times Roman", 11))
                model.appendRow(item)
            self.list_view.setModel(model)

    def on_button_filtro_tipo_clicked(self):
        # Crea un QDialog personalizzato
        dialog = QDialog(self)
        dialog.setWindowTitle("SupplyChain")

        layout = QVBoxLayout(dialog)

        # Crea una QComboBox e aggiungi le opzioni
        combo = QComboBox(dialog)
        options = ["Agricola", "Trasportatore", "Trasformatore", "Rivenditore"]
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
                self.tipo_filtro = selected_option.strip()
                self.nome_filtro = ''
                self.ordinata = False
                self.genera_lista_filtrata_tipo(self.tipo_filtro)
                dialog.accept()

        # Collega i pulsanti alle funzioni
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        # Mostra il dialogo
        dialog.exec_()

    def on_button_filtro_nome_clicked(self):
        while True:
            text, ok = QInputDialog.getText(self, 'SupplyChain', "Inserisci il nome dell'azienda:")

            if not ok:
                break

            if text.strip() == "":
                QMessageBox.warning(self, 'Errore', 'Devi inserire qualcosa!')
                continue

            else:
                self.nome_filtro = text.strip()
                self.tipo_filtro = ''
                self.ordinata = False
                self.genera_lista_filtrata_nome(self.nome_filtro)
                break

    def on_button_ordina_clicked(self):
        self.ordinata = True
        self.nome_filtro = ''
        self.tipo_filtro = ''
        lista_ordinata = self.controller.lista_aziende_ordinata_co2()
        model = QStandardItemModel()
        for f in lista_ordinata:
            saldo = f[2] - f[1]
            if saldo < 0:
                saldo = f"({-saldo})"
            item = QStandardItem(f"Nome Azienda: {f[0][3]}\nSaldo CO2: {saldo}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def on_button_reset_clicked(self):
        self.genera_lista()

    def info(self):
        global azienda
        selected_index = self.list_view.selectedIndexes()

        if selected_index:
            selected_item = selected_index[0].row()  # Ottieni l'indice dell'elemento selezionato
            if self.tipo_filtro == '' and self.nome_filtro == '' and not self.ordinata:
                azienda = self.controller.lista_aziende()[selected_item]
            else:
                if not self.ordinata:
                    if self.nome_filtro == '':
                        azienda = self.controller.lista_aziende_filtro_tipo(self.tipo_filtro)[
                            selected_item
                        ]
                    elif self.tipo_filtro == '':
                        azienda = self.controller.azienda_by_nome(self.nome_filtro)[
                            selected_item
                        ]
                else:
                    azienda = self.controller.lista_aziende_ordinata_co2()[selected_item]

            saldo = azienda[2] - azienda[1]
            if saldo < 0:
                saldo = f"({-saldo})"
            QMessageBox.information(self, "SupplyChain",
                                    f"Azienda selezionata:\n"
                                    f"Nome: {azienda[0][3]}\n"
                                    f"Tipo: {azienda[0][1]}\n"
                                    f"Indirizzo: {azienda[0][2]}\n"
                                    f"CO2 compensata: {azienda[2]}\n"
                                    f"CO2 consumata: {azienda[1]}\n"
                                    f"Saldo CO2: {saldo}")
        else:
            QMessageBox.warning(self, "Nessuna selezione", "Nessun item è stato selezionato.")
