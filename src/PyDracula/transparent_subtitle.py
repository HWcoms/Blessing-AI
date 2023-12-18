import sys
import time

from PySide6 import QtWidgets, QtCore  # must need # noqa
from PySide6.QtWidgets import QApplication, QMainWindow

from PySide6.QtCore import Qt, QSize, QThread, Signal

# # Loading Methods
# module_folder = os.path.join(os.path.dirname(__file__), 'dracula_modules')
# print(module_folder)
# sys.path.append(module_folder)
from sub_modules.ui_transparent_subtitle import Ui_SubtitleWindow

# offset_size_x = 30  # padding
# offset_size_y = 10

offset_pos_y = 0.1  # percent from bottom
maximum_width_percent = .8  # maximum width (percent of screen width)
maximum_height_percent = .5

window_alpha = 0.7
text_color = "255, 255, 255, 255"
bg_color = "0, 0, 0, 200"

text = 'this isessage\n yes hello good! \nmy name is good this is test testetest test tertse'
type_duration = 1
wait_duration = 2


# Subtitle Window
class Subtitle_Window(QMainWindow):
    resize_signal = Signal(str, bool)

    def __init__(self, subtitle_text, type_duration, wait_duration):
        QMainWindow.__init__(self)
        screen = QApplication.primaryScreen()

        self.screen_size = screen.size()

        self.main = None
        self.ui = Ui_SubtitleWindow()
        self.ui.setupUi(self)

        ## UI Settings
        ######################################################################################

        self.setAttribute(Qt.WA_TranslucentBackground)  # Transparent Window
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Mouse Event Through
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Frameless Window & AlwaysOnTop

        self.change_alpha(window_alpha)
        self.resize_signal.connect(self.resize_window_by_text)

        self.ui.label_text.clear()

        # self.ui.label_text = WrappedLabel('test', self)

        # Create WrappedLabel (to get label size after WordWrap)
        self.maximumWidth = self.get_maximum_width()
        self.maximumHeight = self.get_maximum_height()

        self.richtext_html_base = '''
                <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                <html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">
                p, li { white-space: pre-wrap; }
                hr { height: 1px; border-width: 0; }
                li.unchecked::marker { content: "\2610"; }
                li.checked::marker { content: "\2612"; }
                </style></head><body style=" font-family:'Verdana'; font-size:9pt; font-weight:400; font-style:normal;">
                '''
        self.current_richtext = ''
        # self.resize_window_by_text(
        #     'this isessage yes hello good my name is good this is test testetest test tertse')

        ## Show
        #######################################################################################
        self.show()
        # self.display_text(subtitle_text, type_duration)
        dsp_text = DisplayText(self, subtitle_text, type_duration)
        dsp_text.start()

        self.destroy_subtitle(type_duration, wait_duration)

    def change_alpha(self, value: float):
        if value > 1.0:
            value = 1.0
        elif value < 0:
            value = 0

        self.setWindowOpacity(value)

    def resize_window_by_text(self, char, is_new_line: bool = False):
        if not is_new_line:
            self.current_richtext += char

        line_html = '''\n<p align="center" style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:34pt; 
        color:rgba(%s);
        background-color:rgba(%s);">%s</span></p></body></html>'''
        modified_line_html = line_html % (text_color, bg_color, self.current_richtext)  # fgcolor, bgcolor, text

        new_richtext_html = self.richtext_html_base + modified_line_html

        if is_new_line:
            self.richtext_html_base += modified_line_html
            self.current_richtext = ''
            # print(self.richtext_html_base)
            return

        self.ui.label_text.setText(new_richtext_html)

        self.ui.label_text.setFixedSize(QSize(self.maximumWidth, self.maximumHeight))

        self.resize(self.ui.label_text.size())

        for comp in [self.ui.label_text]:
            comp.move(0, 0)

        self.center_on_screen()

    def center_on_screen(self):
        screen_size = self.screen_size

        # Center horizontally
        center_x = (screen_size.width() - self.width()) / 2

        # 200 pixels above the bottom
        center_y = screen_size.height() - int(offset_pos_y * screen_size.height()) - self.height()

        self.move(center_x, center_y)

    def get_maximum_width(self):
        screen_size_width = self.screen_size.width()
        return screen_size_width * maximum_width_percent

    def get_maximum_height(self):
        screen_size_height = self.screen_size.height()
        return screen_size_height * maximum_height_percent

    def destroy_subtitle(self, type_anim_dur, wait_dur):  # Destroy after [type_anim_dur + wait_dur]
        QtCore.QTimer.singleShot((type_anim_dur + wait_dur) * 1000, self.close)
        # QtCore.QTimer.singleShot((type_anim_dur + wait_dur) * 1000, lambda :print("destroyed"))

    def display_text(self, sub_text, duration):
        interval = duration / len(sub_text)

        self.ui.label_text.clear()
        for char in sub_text:
            new_line = False
            if char == '\n':
                new_line = True
            # self.resize_signal.emit(char, new_line)
            self.resize_window_by_text(char, new_line)
            QThread.msleep(int(interval * 1000))  # sleep in milliseconds

            # time.sleep(0.01)
            # print("1")


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
            new_line = False
            if char == '\n':
                new_line = True
            self.parent.resize_signal.emit(char, new_line)
            self.msleep(int(interval * 1000))  # sleep in milliseconds
            # QApplication.processEvents()
            # time.sleep(int(interval) * 0.001)


if __name__ == "__main__":
    # create the application and the main window
    app = QApplication(sys.argv)
    window = Subtitle_Window(text, type_duration, wait_duration)
    sys.exit(app.exec())
