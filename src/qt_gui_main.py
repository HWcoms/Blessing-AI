import sys
import time

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QSizePolicy, \
    QGraphicsDropShadowEffect
from PySide6.QtGui import QIcon, QPixmap, QTransform, QColor

from PySide6.QtCore import Qt, QPoint, QRect, QTimer

# Loading Methods
from modules.ui_splash_screen_scripts import load, background_load, splash_ui_load

from modules.ui_splash_screen import Ui_QSplashScreen
from modules.ui_main_screen import Ui_MainWindow
from PyDracula.main import MainWindow

# Main Application
# class MainWindow(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)


# Splash Screen
class SplashWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main = None
        self.ui = Ui_QSplashScreen()
        self.ui.setupUi(self)

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

        ## Qtimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(35)

        ## Show
        #######################################################################################
        self.show()

    def callMainWindow(self):
        self.timer.stop()

        # Show Main Window
        self.main = MainWindow()
        self.main.show()

        # Close Splash Screen
        self.close()

    def progress(self):
        splash_ui_load(self)


if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)

    window = SplashWindow()
    # window.show()

    # mainWindow = MainWindow()

    # mainWindow.showMinimized()
    # mainWindow.hide()
    # window.background()
    # background_load(window)

    exit(app.exec())
