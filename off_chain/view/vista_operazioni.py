from datetime import datetime

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout, QPushButton, QMenu, \
    QDialog, QDialogButtonBox, QMessageBox, QDateEdit

from off_chain.view import funzioni_utili
from off_chain.view.inserisci_operazione import VistaInserisciOperazione


def stringa_giusta(f, is_storico, scarto):
    if is_storico:
        return (f"Operazione N. {f[0]}\n"
                f"Azienda: {f[1]}\n"
                f"Prodotto: {f[2]}\n"
                f"Data: {f[3]}\n"
                f"CO2 consumata: {f[4]}\n"
                f"Tipo operazione: {f[5]}\n"
                f"Scarto CO2 consumata: {str(scarto)}")
    return (f"Operazione N. {f[0]}\n"
            f"Id Prodotto: {f[1]}\n"
            f"Nome Prodotto: {f[2]}\n"
            f"Quantità Prodotto: {f[3]}\n"
            f"Data: {f[4]}\n"
            f"CO2 consumata: {f[5]}\n"
            f"Tipo operazione: {f[6]}\n"
            f"Scarto CO2 consumata: {scarto}")


class VistaOperazioni(QMainWindow):
    def __init__(self, controller, azienda=(), is_storico=False, prodotto=()):
        super().__init__()

        # self.callback = callback
        self.controller = controller
        self.inserisci_operazione = None
        self.azienda = azienda
        self.is_storico = is_storico
        self.prodotto = prodotto

        # Bisogna cambiare le stringhe nelle list view
        if not is_storico:
            self.lista_operazioni = self.controller.lista_operazioni(self.azienda[0])
        else:
            self.lista_operazioni = self.controller.lista_operazioni_prodotto(self.prodotto[0][0])

        self.data_inizio_filtro = ''
        self.data_fine_filtro = ''
        self.ordinata = False

        # Elementi di layout
        self.list_view = QListView()
        self.aggiungi_button = QPushButton("Aggiungi operazione")
        self.info_button = QPushButton("Visualizza informazioni operazione")
        self.button_filtro = QPushButton("Filtri")
        self.totale_label = QLabel()

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

        label = QLabel("Lista operazioni")

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
                ("Ordina per consumi di CO2", self.on_button_ordina_clicked),
                ("Resetta filtro", self.on_button_reset_clicked),
            ],
            self.button_filtro
        )

        if not self.is_storico:
            main_layout.addLayout(button_layout)
        else:
            label.setText(f"Operazioni effettuate per la produzione\n"
                          f"del seguente prodotto:\n"
                          f"ID: {str(self.prodotto[0][0])}, "
                          f"Nome: {str(self.prodotto[0][1])}")
            self.totale_label.setText(f"Totale co2 consumata: {str(self.prodotto[1])}")
            funzioni_utili.insert_label(self.totale_label, main_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def aggiungi(self):
        self.inserisci_operazione = VistaInserisciOperazione(self.genera_lista, self.azienda)
        self.inserisci_operazione.show()

    def lista_giusta(self, is_storico, ordinata=False, d1=None, d2=None):
        if is_storico:
            return self.controller.lista_operazioni_prodotto(self.prodotto[0][0])
        else:
            if not ordinata and not d1 and not d2:
                return self.controller.lista_operazioni(self.azienda[0])
            if ordinata and not d1 and not d2:
                return self.controller.lista_operazioni_ordinata_co2(self.azienda[0])
            if not ordinata and d1 and d2:
                return self.controller.lista_operazioni_per_data(self.azienda[0], d1, d2)

    def genera_lista(self):
        self.data_inizio_filtro = ''
        self.data_fine_filtro = ''
        self.ordinata = False
        model = QStandardItemModel()
        for f in self.lista_giusta(self.is_storico):
            if self.is_storico:
                scarto = self.controller.scarto_soglia(f[4], f[5], f[2])
            else:
                scarto = self.controller.scarto_soglia(f[5], f[6], f[2])
            item = QStandardItem(stringa_giusta(f, self.is_storico, scarto))
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def genera_lista_filtrata_data(self, data_inizio, data_fine):
        # data_inizio = datetime.strptime(data_inizio, "%d/%m/%Y")
        # data_fine = datetime.strptime(data_fine, "%d/%m/%Y")
        lista_by_data = self.lista_giusta(self.is_storico, d1=data_inizio, d2=data_fine)
        if len(lista_by_data) == 0:
            QMessageBox.information(
                self, 'SupplyChain', f'Non ci sono operazioni nel periodo indicato!')
            self.genera_lista()
        else:
            model = QStandardItemModel()
            for f in lista_by_data:
                if self.is_storico:
                    scarto = self.controller.scarto_soglia(f[4], f[5], f[2])
                else:
                    scarto = self.controller.scarto_soglia(f[5], f[6], f[2])
                item = QStandardItem(stringa_giusta(f, self.is_storico, scarto))
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
        lista_ordinata = self.lista_giusta(self.is_storico, ordinata=True)
        model = QStandardItemModel()
        for f in lista_ordinata:
            if self.is_storico:
                scarto = self.controller.scarto_soglia(f[4], f[5], f[2])
            else:
                scarto = self.controller.scarto_soglia(f[5], f[6], f[2])
            item = QStandardItem(stringa_giusta(f, self.is_storico, scarto))
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def on_button_reset_clicked(self):
        self.genera_lista()

    def info(self):
        global operazione
        selected_index = self.list_view.selectedIndexes()

        if selected_index:
            selected_item = selected_index[0].row()  # Ottieni l'indice dell'elemento selezionato
            if self.data_fine_filtro == '' and self.data_inizio_filtro == '' and not self.ordinata:
                operazione = self.lista_giusta(self.is_storico)[selected_item]
            else:
                if not self.ordinata:
                    operazione = self.lista_giusta(
                        self.is_storico, d1=self.data_inizio_filtro, d2=self.data_fine_filtro
                    )[selected_item]
                else:
                    operazione = self.lista_giusta(self.is_storico, ordinata=True)[selected_item]

            if self.is_storico:
                scarto = self.controller.scarto_soglia(operazione[4], operazione[5], operazione[2])
            else:
                scarto = self.controller.scarto_soglia(operazione[5], operazione[6], operazione[2])
            QMessageBox.information(self, "SupplyChain",
                                    stringa_giusta(operazione, self.is_storico, scarto))

        else:
            QMessageBox.warning(self, "Nessuna selezione", "Nessun item è stato selezionato.")
