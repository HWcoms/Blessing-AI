import os
import sys

from PySide6 import QtWidgets  # must need
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect, QMessageBox
from PySide6.QtGui import QColor

from PySide6.QtCore import Qt, QTimer

# Loading Methods
from modules.ui_splash_screen_scripts import splash_ui_load, init_loading_GUI

from modules.ui_splash_screen import Ui_QSplashScreen


# Splash Screen
class SplashWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main = None
        self.ui = Ui_QSplashScreen()
        self.ui.setupUi(self)

        init_loading_GUI(self.ui)  # Initialize values and images from GUI components

        ## UI Settings
        ######################################################################################
        self.setWindowOpacity(0.95)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        ## Drop Shadow Effect
        #######################################################################################
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        ## Qtimer (thread)
        #######################################################################################
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(35)

        ## Show
        #######################################################################################
        self.show()

    def progress(self):
        splash_ui_load(self)

    ## Error Handler
    #######################################################################################
    @staticmethod
    def error_button(button):
        import signal
        if button.text() == "OK":
            os.kill(os.getpid(), signal.SIGTERM)

    def error_message(self):
        msg = QMessageBox()
        msg.setText("<p align='center'> Failed to import module.<br>Ok to Quit Program. </p>")
        msg.setIcon(QMessageBox.Icon.Warning)
        # msg.setInformativeText("Informative Text")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.buttonClicked.connect(self.error_button)
        msg.exec()

    ## Finish Loading Handler
    #######################################################################################
    def callMainWindow(self):
        from PyDracula.main import MainWindow   # using loaded package
        self.timer.stop()

        # Show Main Window
        self.main = MainWindow()
        self.main.show()

        # Close Splash Screen
        self.close()


if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)

    window = SplashWindow()

    exit(app.exec())
