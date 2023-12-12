import sys
import time

from PySide6 import QtWidgets  # must need # noqa
from PySide6.QtWidgets import QApplication, QMainWindow, QSizePolicy
from PySide6.QtGui import QFontMetrics

from PySide6.QtCore import Qt, QSize, QThread, QTimer, Signal

# # Loading Methods
# module_folder = os.path.join(os.path.dirname(__file__), 'dracula_modules')
# print(module_folder)
# sys.path.append(module_folder)
from sub_modules.ui_transparent_subtitle import Ui_SubtitleWindow

offset_size_x = 30
offset_size_y = 10

offset_pos_y = 0.1  # percent from bottom
maximum_width_percent = 0.8


# Subtitle Window
class Subtitle_Window(QMainWindow):
    resize_signal = Signal(str)

    def __init__(self):
        QMainWindow.__init__(self)
        screen = app.primaryScreen()
        self.screen_size = screen.size()

        self.main = None
        self.ui = Ui_SubtitleWindow()
        self.ui.setupUi(self)

        self.bg_color = "255, 255, 255"
        self.bg_alpha = 1.0
        self.text_color = "255, 0, 0"
        # init_loading_GUI(self.ui)  # Initialize values and images from GUI components

        ## UI Settings
        ######################################################################################
        #
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.change_alpha(1.0)
        self.resize_signal.connect(self.resize_window_by_text)

        self.ui.label_text.clear()
        self.ui.label_text.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.ui.label_text.setMaximumWidth(10)
        self.resize_window_by_text(
            'this is test message, this is test message, this is test message, this is test message, this is test message')

        # dsp_text = DisplayText(self, 'this is just test', 1)
        # dsp_text.start()
        ## Show
        #######################################################################################
        self.show()

    def change_alpha(self, value: float):
        if value > 1.0:
            value = 1.0
        elif value < 0:
            value = 0

        self.setWindowOpacity(value)
        self.ui.sub_frame.setStyleSheet("QFrame {"
                                        f"background-color: rgba({self.bg_color},{self.bg_alpha});"
                                        f"color: rgba(f{self.text_color},{255})"
                                        "}")

    def resize_window_by_text(self, char):
        font = self.ui.label_text.font()
        font_metrics = QFontMetrics(font)

        next_str = self.ui.label_text.text() + char
        self.ui.label_text.setText(next_str)

        text_size = font_metrics.size(0, self.ui.label_text.text())

        # if maximum size over adjust todo:
        self.ui.label_text.setFixedSize(QSize(800, self.size().height()))


        print(self.ui.label_text.size())
        text_size = text_size + QSize(offset_size_x, offset_size_y)
        # print(text_size)

        # resize to font_metrics & move 0, 0
        self.resize(text_size)
        for comp in [self.ui.frame_bg, self.ui.label_text]:
            comp.setFixedSize(text_size)
            comp.move((self.size().width() / 2) - (text_size.width() / 2),
                      (self.size().height() / 2) - (text_size.height() / 2))

        self.center_on_screen()

    def center_on_screen(self):
        screen_size = self.screen_size

        # Center horizontally
        center_x = (screen_size.width() - self.width()) / 2

        # 200 pixels above the bottom
        center_y = screen_size.height() - int(offset_pos_y * screen_size.height()) - self.height()

        self.move(center_x, center_y)

    def check_maximum(self, str):
        font = self.ui.label_text.font()
        font_metrics = QFontMetrics(font)
        screen_size = self.screen_size

        modified_string = str

        while True:
            text_size = font_metrics.size(0, modified_string)
            text_size += QSize(offset_size_x, offset_size_y)
            if text_size.width() < screen_size.width():
                break
            # Split the string into words

            # Add a newline between the last and second-to-last words
            words = modified_string.split()
            modified_text = ' '.join(words[:-1]) + '\n' + words[-1]
            print(words[:-1], words[-1])
            time.sleep(0.5)

            # print(text_size)

        return modified_string


class DisplayText(QThread):
    def __init__(self, parent, text, duration):
        super().__init__(parent)
        self.parent = parent
        self.text = text
        self.duration = duration

    def run(self):
        interval = self.duration / len(self.text)

        self.parent.ui.label_text.clear()

        for char in self.text:
            self.parent.resize_signal.emit(char)
            self.msleep(int(interval * 1000))  # sleep in milliseconds
            QApplication.processEvents()


if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = Subtitle_Window()
    sys.exit(app.exec())
