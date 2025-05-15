# pylint: disable=no-name-in-module
# pylint: disable=import-error

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QDesktopWidget, QAction, QFormLayout, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QListView, QMenu, QMenuBar
)


def is_blank(values: list[str]) -> bool:
    """Controlla se la lista contiene stringhe vuote o spazi."""
    return any(val.strip() == '' for val in values)


def center(window) -> None:
    """Centra la finestra sullo schermo."""
    geometry = window.frameGeometry()
    center_point = QDesktopWidget().availableGeometry().center()
    geometry.moveCenter(center_point)
    window.move(geometry.topLeft())


def add_field_to_form(label: QLabel, field: QLineEdit, form: QFormLayout) -> None:
    """Aggiunge un campo di input con label a un layout di form."""
    field.setStyleSheet("border-radius: 10px; border: 2px solid green; color: black; padding: 5px")
    label.setFont(QFont("Times Roman", 11, QFont.Bold))
    label.setStyleSheet("color: green")
    form.addRow(label, field)


def insert_button(button: QPushButton, layout: QVBoxLayout | QHBoxLayout) -> None:
    """Inserisce un pulsante in un layout verticale o orizzontale."""
    button.setFont(QFont("Times Roman", 11, QFont.Bold))
    button.setStyleSheet("background-color: green; border-radius: 15px; color: white; padding: 10px")
    layout.addWidget(button)


def insert_button_in_grid(
    button: QPushButton,
    layout: QGridLayout,
    row: int,
    col: int,
    sviluppatori: bool = False
) -> None:
    """Inserisce un pulsante in un layout a griglia."""
    font = QFont("Times Roman", 11, QFont.Bold)
    button.setFont(font)

    if sviluppatori:
        style = (
            "background-color: transparent; border-radius: 55px; border: 2px solid black; padding: 5px"
        )
    else:
        style = (
            "background-color: green; border-radius: 15px; color: white; padding: 10px"
        )

    button.setStyleSheet(style)
    layout.addWidget(button, row, col)


def insert_label(label: QLabel, layout: QVBoxLayout | QHBoxLayout, dim: int = 20, color: str = "color: green") -> None:
    """Inserisce una label in un layout con stile personalizzato."""
    label.setAlignment(Qt.AlignCenter)
    label.setFont(QFont("Times Roman", dim, QFont.Bold))
    label.setStyleSheet(color)
    layout.addWidget(label, alignment=Qt.AlignCenter)


def insert_logo(logo: QLabel, layout: QGridLayout, pixmap: QPixmap) -> None:
    """Inserisce un logo (immagine) in un layout a griglia."""
    logo.setPixmap(pixmap)
    logo.setScaledContents(True)
    logo.setFixedSize(150, 150)
    layout.addWidget(logo, 3, 3)


def insert_list(list_widget: QListView, layout: QVBoxLayout | QHBoxLayout, width: int = 500, height: int = 400) -> None:
    """Inserisce una lista in un layout con dimensioni predefinite."""
    list_widget.setFixedSize(width, height)
    list_widget.setStyleSheet(stile_liste())
    layout.addWidget(list_widget, alignment=Qt.AlignCenter)


def stile_checkbox() -> str:
    """Restituisce lo stile CSS per una checkbox."""
    return """
        QCheckBox {
            background-color: green;
            border-radius: 15px;
            padding: 2px;
        }
        QCheckBox::indicator {
            width: 26px;
            height: 26px;
            border-radius: 13px;
            background-color: white;
        }
        QCheckBox::indicator:checked {
            background-color: white;
            left: 30px;
        }
        QCheckBox::indicator:unchecked {
            background-color: white;
            left: 2px;
        }
    """


def stile_liste() -> str:
    """Restituisce lo stile CSS per una QListView."""
    return """
        QListView {
            background-color: white;
            border: 1px solid green;
            border-radius: 15px;
        }
        QListView::item {
            background-color: white;
            border-radius: 10px;
            margin: 10px 10px 0 10px;
            border: 1px solid green;
            padding: 5px;
        }
        QListView::item:selected {
            background-color: lightgreen;
            color: black;
        }
    """


def config_widget(
    main_layout: QVBoxLayout,
    label: QLabel,
    form_layout: QFormLayout,
    form_container: QVBoxLayout,
    margin: int,
    dim: int = 40
) -> None:
    """Configura un widget form con margini e stile predefinito."""
    main_layout.setSpacing(20)
    main_layout.setAlignment(Qt.AlignCenter)

    insert_label(label, main_layout, dim)
    form_layout.setSpacing(10)
    form_container.addLayout(form_layout)
    form_container.setContentsMargins(margin, 0, margin, 0)


def config_menu(menu: QMenu, items: list[tuple[str, callable]], button: QPushButton) -> None:
    """Aggiunge voci a un menu e lo collega a un pulsante."""
    for text, action in items:
        menu.addAction(text, action)
    button.setMenu(menu)


def config_menubar(
    parent,
    menu_title: str,
    icon_path: str,
    action_text: str,
    shortcut: str,
    menubar: QMenuBar
) -> QAction:
    """Configura una voce nella menubar con icona e scorciatoia."""
    action = QAction(QIcon(icon_path), action_text, parent=parent)
    action.setShortcut(shortcut)
    menubar.addMenu(menu_title).addAction(action)
    return action
