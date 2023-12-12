# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'transparent_subtitleUgiYhn.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QMainWindow,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_SubtitleWindow(object):
    def setupUi(self, SubtitleWindow):
        if not SubtitleWindow.objectName():
            SubtitleWindow.setObjectName(u"SubtitleWindow")
        SubtitleWindow.resize(1078, 378)
        SubtitleWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(SubtitleWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.sub_frame = QFrame(self.centralwidget)
        self.sub_frame.setObjectName(u"sub_frame")
        self.sub_frame.setFrameShape(QFrame.StyledPanel)
        self.sub_frame.setFrameShadow(QFrame.Raised)
        self.frame_bg = QFrame(self.sub_frame)
        self.frame_bg.setObjectName(u"frame_bg")
        self.frame_bg.setGeometry(QRect(170, 90, 641, 161))
        self.frame_bg.setStyleSheet(u"background-color: yellow")
        self.frame_bg.setFrameShape(QFrame.StyledPanel)
        self.frame_bg.setFrameShadow(QFrame.Raised)
        self.label_text = QLabel(self.sub_frame)
        self.label_text.setObjectName(u"label_text")
        self.label_text.setGeometry(QRect(130, 10, 941, 361))
        font = QFont()
        font.setPointSize(35)
        self.label_text.setFont(font)
        self.label_text.setStyleSheet(u"background-color: transparent")
        self.label_text.setAlignment(Qt.AlignCenter)
        self.label_text.setWordWrap(True)

        self.verticalLayout.addWidget(self.sub_frame)

        SubtitleWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SubtitleWindow)

        QMetaObject.connectSlotsByName(SubtitleWindow)
    # setupUi

    def retranslateUi(self, SubtitleWindow):
        SubtitleWindow.setWindowTitle(QCoreApplication.translate("SubtitleWindow", u"SubTitle", None))
        self.label_text.setText(QCoreApplication.translate("SubtitleWindow", u"Testing testing Testing testing", None))
    # retranslateUi

