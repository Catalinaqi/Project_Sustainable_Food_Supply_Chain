from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMessageBox

from presentation.view import funzioni_utili

"eliminabile"
class VistaSviluppatori(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("presentation\\resources\\logo_centro.png"))

        # Elementi di layout
        self.logo = QLabel()

        self.button_inzaghi = QPushButton()
        self.button_inzaghi.setIcon(QIcon("presentation\\resources\\inzaghi.png"))
        self.button_inzaghi.setIconSize(QSize(100, 100))

        self.button_conte = QPushButton()
        self.button_conte.setIcon(QIcon("presentation\\resources\\conte.png"))
        self.button_conte.setIconSize(QSize(100, 100))

        self.button_conceicao = QPushButton()
        self.button_conceicao.setIcon(QIcon("presentation\\resources\\conceicao.png"))
        self.button_conceicao.setIconSize(QSize(100, 100))

        self.button_ranieri = QPushButton()
        self.button_ranieri.setIcon(QIcon("presentation\\resources\\domenico.png"))
        self.button_ranieri.setIconSize(QSize(100, 100))

        self.button_mourinho = QPushButton()
        self.button_mourinho.setIcon(QIcon("presentation\\resources\\mourinho.png"))
        self.button_mourinho.setIconSize(QSize(100, 100))

        self.button_thiago = QPushButton()
        self.button_thiago.setIcon(QIcon("presentation\\resources\\thiago.png"))
        self.button_thiago.setIconSize(QSize(100, 100))

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SupplyChain')
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(50)
        main_layout.setAlignment(Qt.AlignCenter)

        button_layout = QGridLayout()
        button_layout.setSpacing(1)

        funzioni_utili.insert_button_in_grid(self.button_inzaghi, button_layout, 1, 2, True)
        self.button_inzaghi.clicked.connect(self.show_inzaghi)

        funzioni_utili.insert_button_in_grid(self.button_conte, button_layout, 1, 4, True)
        self.button_conte.clicked.connect(self.show_conte)

        funzioni_utili.insert_button_in_grid(self.button_conceicao, button_layout, 3, 1, True)
        self.button_conceicao.clicked.connect(self.show_conceicao)

        funzioni_utili.insert_button_in_grid(self.button_ranieri, button_layout, 3, 5, True)
        self.button_ranieri.clicked.connect(self.show_ranieri)

        funzioni_utili.insert_button_in_grid(self.button_mourinho, button_layout, 5, 2, True)
        self.button_mourinho.clicked.connect(self.show_mourinho)

        funzioni_utili.insert_button_in_grid(self.button_thiago, button_layout, 5, 4, True)
        self.button_thiago.clicked.connect(self.show_thiago)

        funzioni_utili.insert_logo(self.logo, button_layout, QPixmap("presentation\\resources\\logo_centro.png"))

        main_layout.addLayout(button_layout)

        outer_layout.addLayout(main_layout)

        funzioni_utili.center(self)

    def show_inzaghi(self):
        QMessageBox.information(self, "Sviluppatore", "Inzaghi")

    def show_conte(self):
        QMessageBox.information(self, "Sviluppatore", "Conte")

    def show_conceicao(self):
        QMessageBox.information(self, "Sviluppatore", "Conceicao")

    def show_ranieri(self):
        QMessageBox.information(self, "Sviluppatore", "Ranieri")

    def show_mourinho(self):
        QMessageBox.information(self, "Sviluppatore", "Mourinho")

    def show_thiago(self):
        QMessageBox.information(self, "Sviluppatore", "Thiago")
