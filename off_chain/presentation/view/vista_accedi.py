# pylint: disable=no-name-in-module
# pylint: disable=import-error

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QMainWindow, QAction,
    QCheckBox, QStackedWidget, QComboBox, QMessageBox, QLabel,
    QLineEdit, QPushButton
)

from presentation.controller.credential_controller import ControllerAutenticazione
from presentation.view import funzioni_utili
from presentation.view.home_page_aziende import HomePage
from presentation.view.home_page_certificatore import HomePageCertificatore
from presentation.view.home_page_guest import HomePageGuest
from session import Session


class VistaAccedi(QMainWindow):
    """Main authentication view managing login and registration sections."""

    def __init__(self):
        super().__init__()
        self.controller = ControllerAutenticazione()
        self.home_certificatore = None
        self.home_page = None
        self.home_guest = None

        self.setWindowIcon(QIcon("presentation/resources/logo_centro.png"))

        # Login UI elements
        self.login_label = QLabel("Login")
        self.section_switcher = QCheckBox()
        self.register_label = QLabel("Registrati")
        self.stacked_widget = QStackedWidget()

        self.username_label = QLabel("Nome Utente:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.login_button = QPushButton("Accedi")
        self.guest_button = QPushButton("Entra come guest")
        self.logo = QLabel()

        # Registration UI elements
        self.username_label_reg = QLabel("Nome Utente:")
        self.username_input_reg = QLineEdit()
        self.tipo_label = QLabel("Tipo Azienda:")
        self.tipo_input = QComboBox()
        self.indirizzo_label = QLabel("Indirizzo:")
        self.indirizzo_input = QLineEdit()
        self.password_label_reg = QLabel("Password:")
        self.password_input_reg = QLineEdit()
        self.conferma_password_label = QLabel("Conferma Password:")
        self.conferma_password_input = QLineEdit()
        self.tcu_cb = QCheckBox("Ho letto e accetto i termini e le condizioni d'uso")
        self.tcu_label = QLabel("Visualizza i termini e le condizioni d'uso")
        self.register_button = QPushButton("Registrati")

        # Password visibility control
        self.password_fields = [
            self.password_input,
            self.password_input_reg,
            self.conferma_password_input
        ]
        self.icons_action = []
        self.password_visible = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup the main UI layout and components."""
        self.setWindowTitle("SupplyChain")
        self.setGeometry(0, 0, 750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setAlignment(Qt.AlignCenter)

        # Section switcher layout
        switcher_layout = QHBoxLayout()
        switcher_layout.setAlignment(Qt.AlignCenter)

        self.login_label.setFont(QFont("Times Roman", 11, QFont.Bold))
        self.login_label.setStyleSheet("color: green")

        self.section_switcher.setFixedSize(60, 30)
        self.section_switcher.setStyleSheet(funzioni_utili.stile_checkbox())
        self.section_switcher.stateChanged.connect(self.switch_section)

        self.register_label.setFont(QFont("Times Roman", 11, QFont.Bold))
        self.register_label.setStyleSheet("color: green")

        switcher_layout.addWidget(self.login_label)
        switcher_layout.addWidget(self.section_switcher)
        switcher_layout.addWidget(self.register_label)

        switcher_container = QVBoxLayout()
        switcher_container.addLayout(switcher_layout)
        switcher_container.setAlignment(Qt.AlignCenter)

        self.stacked_widget.setFixedWidth(600)
        stacked_container = QVBoxLayout()
        stacked_container.addWidget(self.stacked_widget, alignment=Qt.AlignCenter)
        stacked_container.setAlignment(Qt.AlignCenter)

        outer_layout.addLayout(stacked_container)
        outer_layout.addLayout(switcher_container)

        # Initialize login and registration widgets
        login_widget = QWidget()
        self._init_login_ui(login_widget)
        self.stacked_widget.addWidget(login_widget)

        registrati_widget = QWidget()
        self._init_registrati_ui(registrati_widget)
        self.stacked_widget.addWidget(registrati_widget)

        funzioni_utili.center(self)

    def _init_login_ui(self, widget: QWidget):
        """Configure the login section UI."""
        main_layout = QVBoxLayout(widget)

        welcome_label = QLabel("Benvenuto!")
        form_layout = QFormLayout()
        form_container = QVBoxLayout()

        funzioni_utili.config_widget(main_layout, welcome_label, form_layout, form_container, 100)

        funzioni_utili.add_field_to_form(self.username_label, self.username_input, form_layout)

        self.password_input.setEchoMode(QLineEdit.Password)
        funzioni_utili.add_field_to_form(self.password_label, self.password_input, form_layout)

        main_layout.addLayout(form_container)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        self.login_button.clicked.connect(self.accedi)
        funzioni_utili.insert_button(self.login_button, button_layout)

        self.guest_button.clicked.connect(self.entra_guest)
        funzioni_utili.insert_button(self.guest_button, button_layout)

        main_layout.addLayout(button_layout)

        self.logo.setPixmap(QPixmap("presentation/resources/logo_trasparente.png"))
        self.logo.setScaledContents(True)
        self.logo.setFixedSize(300, 300)
        main_layout.addWidget(self.logo, alignment=Qt.AlignCenter)

    def _init_registrati_ui(self, widget: QWidget):
        """Configure the registration section UI."""
        main_layout = QVBoxLayout(widget)

        registrati_label = QLabel("Registrati!")
        form_layout = QFormLayout()
        form_container = QVBoxLayout()

        funzioni_utili.config_widget(main_layout, registrati_label, form_layout, form_container, 100)

        funzioni_utili.add_field_to_form(self.username_label_reg, self.username_input_reg, form_layout)

        self.tipo_input.addItems([
            'Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore'
        ])
        funzioni_utili.add_field_to_form(self.tipo_label, self.tipo_input, form_layout)

        funzioni_utili.add_field_to_form(self.indirizzo_label, self.indirizzo_input, form_layout)

        self.password_input_reg.setEchoMode(QLineEdit.Password)
        funzioni_utili.add_field_to_form(self.password_label_reg, self.password_input_reg, form_layout)

        self.conferma_password_input.setEchoMode(QLineEdit.Password)
        funzioni_utili.add_field_to_form(self.conferma_password_label, self.conferma_password_input, form_layout)

        # Add password visibility toggle actions
        self.icons_action.clear()
        for pwd_field in self.password_fields:
            action = QAction(QIcon("presentation/resources/pass_invisibile.png"), "", pwd_field)
            action.triggered.connect(self.change_password_visibility)
            pwd_field.addAction(action, QLineEdit.TrailingPosition)
            self.icons_action.append(action)

        main_layout.addLayout(form_container)

        main_layout.addWidget(self.tcu_cb, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.tcu_label, alignment=Qt.AlignCenter)

        self.tcu_label.setStyleSheet("color: blue; text-decoration: underline;")
        self.tcu_label.mousePressEvent = self.on_tcu_click

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        self.register_button.clicked.connect(self.registrati)
        funzioni_utili.insert_button(self.register_button, button_layout)

        main_layout.addLayout(button_layout)

    def on_tcu_click(self, event):
        """Show terms and conditions placeholder message."""
        QMessageBox.warning(
            self, "SupplyChain", "Termini e condizioni d'uso work in progress!"
        )

    def switch_section(self, state):
        """Switch between login and registration views."""
        self.stacked_widget.setCurrentIndex(1 if state == Qt.Checked else 0)

    def accedi(self):
        """Handle user login."""
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            utente = self.controller.login(username, password)
            if utente:
                QMessageBox.information(self, "SupplyChain", "Accesso effettuato correttamente!")
                role = Session().current_user.get("role")
                if role == "Certificatore":
                    self.home_certificatore = HomePageCertificatore(self.reset)
                    self.home_certificatore.show()
                else:
                    self.home_page = HomePage(self.reset, utente)
                    self.home_page.show()
                self.setVisible(False)
        except Exception as err:
            QMessageBox.warning(self, "SupplyChain", str(err))

    def entra_guest(self):
        """Allow the user to enter as guest."""
        self.home_guest = HomePageGuest(self.reset)
        QMessageBox.information(self, "SupplyChain", "Puoi entrare come guest!")
        self.home_guest.show()
        self.close()

    def registrati(self):
        """Handle user registration."""
        if not self.tcu_cb.isChecked():
            QMessageBox.warning(self, "SupplyChain", "Devi accettare i termini e le condizioni d'uso!")
            return

        username = self.username_input_reg.text()
        password = self.password_input_reg.text()
        conferma_password = self.conferma_password_input.text()

        if password != conferma_password:
            QMessageBox.warning(self, "SupplyChain", "Le password non corrispondono!")
            return

        try:
            self.controller.register(
                username=username,
                password=password,
                tipo=self.tipo_input.currentText(),
                indirizzo=self.indirizzo_input.text(),
            )
            QMessageBox.information(self, "SupplyChain", "Registrazione avvenuta con successo!")
            self.section_switcher.setChecked(False)
        except Exception as err:
            QMessageBox.warning(self, "SupplyChain", str(err))

    def change_password_visibility(self):
        """Toggle password visibility in password fields."""
        self.password_visible = not self.password_visible
        icon_visible = QIcon("presentation/resources/pass_visibile.png")
        icon_invisible = QIcon("presentation/resources/pass_invisibile.png")
        icon = icon_visible if self.password_visible else icon_invisible

        for pwd_field, action in zip(self.password_fields, self.icons_action):
            pwd_field.setEchoMode(QLineEdit.Normal if self.password_visible else QLineEdit.Password)
            action.setIcon(icon)

    def reset(self):
        """Reset the login and registration fields and show login view."""
        self.username_input.clear()
        self.password_input.clear()
        self.username_input_reg.clear()
        self.password_input_reg.clear()
        self.conferma_password_input.clear()
        self.indirizzo_input.clear()
        self.tipo_input.setCurrentIndex(0)
        self.tcu_cb.setChecked(False)
        self.section_switcher.setChecked(False)
        self.setVisible(True)
