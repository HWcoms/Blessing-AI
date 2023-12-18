# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'transparent_subtitlenMQeqI.ui'
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
        self.label_text = QLabel(self.sub_frame)
        self.label_text.setObjectName(u"label_text")
        self.label_text.setGeometry(QRect(140, 50, 891, 301))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_text.sizePolicy().hasHeightForWidth())
        self.label_text.setSizePolicy(sizePolicy)
        self.label_text.setMinimumSize(QSize(0, 0))
        self.label_text.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setPointSize(35)
        self.label_text.setFont(font)
        self.label_text.setStyleSheet(u"background-color: transparent")
        self.label_text.setAlignment(Qt.AlignBottom|Qt.AlignHCenter)
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

