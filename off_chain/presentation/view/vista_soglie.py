from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QListView, QHBoxLayout,
                             QPushButton, QMessageBox, QDialog, QDialogButtonBox, QComboBox)

from off_chain.presentation.view import funzioni_utili


class VistaSoglie(QMainWindow):
    def __init__(self, certificatore=None):
        super().__init__()

        # self.callback = callback
        self.certificatore = certificatore

        self.lista_prova = [
            ("Produzione", "Pomodori", 50),  # Soglia massima di CO₂: 50
            ("Produzione", "Olio d'oliva", 40),
            ("Trasformazione", "Passata di pomodoro", 30),
            ("Trasformazione", "Pane", 25),
            ("Trasporto", "Pomodori", 60),
            ("Trasporto", "Patate", 55),
            ("Messa su scaffali", "Passata di pomodoro", 20),
            ("Messa su scaffali", "Patatine fritte confezionate", 15),
        ]

        # Elementi di layout
        self.list_view = QListView()
        self.modifica_button = QPushButton("Modifica soglia")

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

        label = QLabel("Lista soglie")

        funzioni_utili.insert_label(label, main_layout)

        funzioni_utili.insert_list(self.list_view, main_layout)
        self.genera_lista()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)  # Centra orizzontalmente

        if self.certificatore:
            funzioni_utili.insert_button(self.modifica_button, button_layout)
        self.modifica_button.clicked.connect(self.modifica)

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def genera_lista(self):
        model = QStandardItemModel()
        for f in self.lista_prova:
            item = QStandardItem(f"Operazione: {f[0]}\n"
                                 f"Prodotto: {f[1]}\n"
                                 f"Soglia CO2: {f[2]}")
            item.setEditable(False)
            item.setFont(QFont("Times Roman", 11))
            model.appendRow(item)
        self.list_view.setModel(model)

    def modifica(self):
        selected_index = self.list_view.selectedIndexes()

        if selected_index:
            selected_item = selected_index[0].row()
            soglia = self.lista_prova[selected_item]

            # Crea un QDialog personalizzato
            dialog = QDialog(self)
            dialog.setWindowTitle("SupplyChain")

            layout = QVBoxLayout(dialog)

            label = QLabel(f'Inserisci la nuova soglia:\n'
                           f'Operazione: {soglia[0]}\n'
                           f'Prodotto: {soglia[1]}\n')
            layout.addWidget(label)

            # Crea una QComboBox e aggiungi le opzioni
            combo = QComboBox(dialog)
            options = [str(i) for i in range(1000)]
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
                    self.lista_prova[selected_item] = (soglia[0], soglia[1], int(selected_option))
                    self.genera_lista()
                    dialog.accept()
                    QMessageBox.information(self, "Nessuna selezione",
                                            "Soglia modificata correttamente")

            # Collega i pulsanti alle funzioni
            buttons.accepted.connect(on_accept)
            buttons.rejected.connect(dialog.reject)

            # Mostra il dialogo
            dialog.exec_()

        else:
            QMessageBox.warning(self, "Nessuna selezione", "Nessun item è stato selezionato.")
