from PySide6 import QtWidgets, QtGui, QtCore
import os

from PySide6.QtWidgets import QSizePolicy

ico_path = os.path.dirname(os.path.dirname(__file__))
ico_path = os.path.join(ico_path, 'PyDracula', 'images', 'icons', 'cil-x-circle-red.png')


class TextWButtonWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, label_text='', button_text=''):
        super(TextWButtonWidget, self).__init__(parent)

        # add your buttons
        layout = QtWidgets.QHBoxLayout()

        # adjust spacings to your needs
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch()

        self.label_widget = QtWidgets.QLabel(label_text)
        layout.addWidget(self.label_widget)

        spacer = QtWidgets.QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)

        ico_size = 15

        self.button_widget = QtWidgets.QPushButton(button_text)
        self.button_widget.setGeometry(0, 0, ico_size, ico_size)
        self.button_widget.setIcon(QtGui.QIcon(ico_path))
        self.button_widget.setIconSize(QtCore.QSize(ico_size, ico_size))
        self.button_widget.setStyleSheet("QPushButton{"
                                    "border: 2px solid rgb(255, 0, 110);"
                                    "background-color: transparent;"
                                    "border-radius: 5px;"
                                    "}"
                                    "QPushButton:hover{background-color: rgb(58, 134, 255);}"
                                    "QPushButton:pressed{background-color: rgb(131, 56, 236);}")
        layout.addWidget(self.button_widget)

        self.setLayout(layout)
