import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap, QTransform

from PySide6.QtCore import Qt, QPoint, QRect

# form_class = uic.loadUiType("blessingaiqt.ui")[0]
from modules.ui_splash_screen_scripts import load, background_load
from modules.ui_splash_screen import Ui_QSplashScreen


class SplashWindow(QMainWindow, Ui_QSplashScreen):
    def __init__(self):
        super(SplashWindow, self).__init__()
        # self.setWindowTitle("Loading Blessing-AI")    #overriding at ui_splash_screen
        self.setWindowOpacity(0.95)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setupUi(self)

    def callMainWindow(self):
        self.hide()
        # new_win.show()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        og_pixmap = QPixmap(u":/Logo/ico/images/blessingAILogo.png")
        og_pixmap = og_pixmap.transformed(QTransform().scale(.3, .3))
        pixmap = og_pixmap.copy(0, 0, 100, 200)
        lbl = QLabel(self)
        lbl.setPixmap(pixmap)

        hbox.addWidget(lbl)
        self.setLayout(hbox)

        self.move(300, 200)
        self.setWindowTitle('Image with PyQt')
        self.show()
        self.resize(854, 518)


if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)

    window = SplashWindow()

    window.show()

    background_load(window)

    exit(app.exec())
