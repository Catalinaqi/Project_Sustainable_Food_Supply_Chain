from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout, QPushButton, QMenu, \
    QDialog, QDialogButtonBox, QMessageBox, QDateEdit

from off_chain.presentation.controller.company_controller import ControllerAzienda
from off_chain.presentation.view import funzioni_utili
from off_chain.presentation.view.inserisci_azione import VistaInserisciAzione


class VistaAzioniCompensative(QMainWindow):
    def __init__(self, azienda):
        super().__init__()

        # self.callback = callback
        self.inserisci_azione = None
        self.azienda = azienda

        self.controller = ControllerAzienda()

        self.data_inizio_filtro = ''
        self.data_fine_filtro = ''
        self.ordinata = False

        # Elementi di layout
        self.list_view = QListView()
        self.aggiungi_button = QPushButton("Aggiungi azione")
        self.info_button = QPushButton("Visualizza informazioni azione")
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

        label = QLabel("Lista azioni compensative")

        funzioni_utili.insert_label(label, main_layout)

        funzioni_utili.insert_list(self.list_view, main_layout)
        self.genera_lista()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)  # Centra orizzontalmente

        funzioni_utili.insert_button(self.aggiungi_button, button_layout)
        self.aggiungi_button.clicked.connect(self.aggiungi)

        funzioni_utili.insert_button(self.info_button, button_layout)
        self.info_button.clicked.connect(self.info)

        funzioni_utili.insert_button(self.button_filtro, button_layout)

        menu_filtri = QMenu()
        funzioni_utili.config_menu(
            menu_filtri,
            [
                ("Cerca per data", self.on_button_filtro_data_clicked),
                ("Ordina per CO2 risparmiata", self.on_button_ordina_clicked),
                ("Resetta filtro", self.on_button_reset_clicked),
            ],
            self.button_filtro
        )

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def aggiungi(self):
        self.inserisci_azione = VistaInserisciAzione(self.genera_lista, self.azienda)
        self.inserisci_azione.show()

    def genera_lista(self):
        self.data_inizio_filtro = ''
        self.data_fine_filtro = ''
        self.ordinata = False
        model = QStandardItemModel()
        lista = self.controller.lista_azioni_compensative(self.azienda[0])
        for f in lista:
            item = QStandardItem(f"Azione N. {f[0]}\n"
                                 f"Data: {f[1]}\n"
                                 f"CO2 risparmiata: {f[3]}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def genera_lista_filtrata_data(self, data_inizio, data_fine):
        lista_by_data = self.controller.lista_azioni_per_data(
            self.azienda[0], data_inizio, data_fine
        )
        if len(lista_by_data) == 0:
            QMessageBox.information(
                self, 'SupplyChain', f'Non ci sono azioni nel periodo indicato!')
            self.genera_lista()
        else:
            model = QStandardItemModel()
            for f in lista_by_data:
                item = QStandardItem(f"Azione N. {f[0]}\n"
                                     f"Data: {f[1]}\n"
                                     f"CO2 risparmiata: {f[3]}")
                item.setEditable(False)
                item.setFont(QFont("Times Roman", 11))
                model.appendRow(item)
            self.list_view.setModel(model)

    def on_button_filtro_data_clicked(self):
        # Crea un QDialog personalizzato
        dialog = QDialog(self)
        dialog.setWindowTitle("EdilGest")

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Da:"))

        # Crea una QDateEdit per la data iniziale
        data1 = QDateEdit(dialog)
        data1.setCalendarPopup(True)
        data1.setDisplayFormat("dd/MM/yyyy")
        data1.setDate(QDate.currentDate())
        layout.addWidget(data1)

        layout.addWidget(QLabel("A:"))

        # Crea una QDateEdit per la data finale
        data2 = QDateEdit(dialog)
        data2.setCalendarPopup(True)
        data2.setDisplayFormat("dd/MM/yyyy")
        data2.setDate(QDate.currentDate())
        layout.addWidget(data2)

        # Aggiungi i pulsanti "Ok" e "Cancel"
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(buttons)

        # Definisci cosa succede quando l'utente clicca su "Ok"
        def on_accept():
            self.ordinata = False
            self.data_inizio_filtro = data1.text()
            self.data_fine_filtro = data2.text()
            self.genera_lista_filtrata_data(self.data_inizio_filtro, self.data_fine_filtro)
            dialog.accept()

        # Collega i pulsanti alle funzioni
        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        # Mostra il dialogo
        dialog.exec_()

    def on_button_ordina_clicked(self):
        self.ordinata = True
        self.data_inizio_filtro = ''
        self.data_fine_filtro = ''
        lista_ordinata = self.controller.lista_azioni_compensative_ordinata(self.azienda[0])
        model = QStandardItemModel()
        for f in lista_ordinata:
            item = QStandardItem(f"Azione N. {f[0]}\n"
                                 f"Data: {f[1]}\n"
                                 f"CO2 risparmiata: {f[3]}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def on_button_reset_clicked(self):
        self.genera_lista()

    def info(self):
        global azione
        selected_index = self.list_view.selectedIndexes()

        if selected_index:
            selected_item = selected_index[0].row()  # Ottieni l'indice dell'elemento selezionato
            if self.data_fine_filtro == '' and self.data_inizio_filtro == '' and not self.ordinata:
                azione = self.controller.lista_azioni_compensative(self.azienda[0])[selected_item]
            else:
                if not self.ordinata:
                    azione = self.controller.lista_azioni_per_data(
                        self.azienda[0], self.data_inizio_filtro, self.data_fine_filtro
                    )[selected_item]
                else:
                    azione = self.controller.lista_azioni_compensative_ordinata(
                        self.azienda[0])[selected_item]

            QMessageBox.information(self, "SupplyChain",
                                    f"Azione N. {azione[0]}\n"
                                    f"Data: {azione[1]}\n"
                                    f"Azienda: {self.azienda[0]}\n"
                                    f"CO2 compensata: {azione[3]}\n"
                                    f"Descrizione: {azione[4]}")

        else:
            QMessageBox.warning(self, "Nessuna selezione", "Nessun item è stato selezionato.")
