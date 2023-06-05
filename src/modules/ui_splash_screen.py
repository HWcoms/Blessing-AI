# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'splash_screenTmZLSJ.ui'
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
import images_rc

class Ui_QSplashScreen(object):
    def setupUi(self, QSplashScreen):
        if not QSplashScreen.objectName():
            QSplashScreen.setObjectName(u"QSplashScreen")
        QSplashScreen.resize(854, 518)
        self.centralwidget = QWidget(QSplashScreen)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        self.centralwidget.setStyleSheet(u"QWidget {\n"
"	background-color: transparent;\n"
"}")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.dropShadoFrame = QFrame(self.centralwidget)
        self.dropShadoFrame.setObjectName(u"dropShadoFrame")
        self.dropShadoFrame.setEnabled(True)
        self.dropShadoFrame.setStyleSheet(u"QFrame {\n"
"	background-color: rgb(56, 58, 89);\n"
"	color: rgb(220, 220, 220);\n"
"	border-radius: 10px\n"
"}")
        self.dropShadoFrame.setFrameShape(QFrame.StyledPanel)
        self.dropShadoFrame.setFrameShadow(QFrame.Raised)
        self.ogTitle = QLabel(self.dropShadoFrame)
        self.ogTitle.setObjectName(u"ogTitle")
        self.ogTitle.setEnabled(False)
        self.ogTitle.setGeometry(QRect(0, 0, 0, 0))
        font = QFont()
        font.setFamilies([u"Noto Sans"])
        font.setPointSize(40)
        self.ogTitle.setFont(font)
        self.ogTitle.setStyleSheet(u"color: rgb(232, 84, 120);")
        self.ogTitle.setAlignment(Qt.AlignCenter)
        self.ProgressTitle = QLabel(self.dropShadoFrame)
        self.ProgressTitle.setObjectName(u"ProgressTitle")
        self.ProgressTitle.setEnabled(True)
        self.ProgressTitle.setGeometry(QRect(0, -30, 841, 461))
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ProgressTitle.sizePolicy().hasHeightForWidth())
        self.ProgressTitle.setSizePolicy(sizePolicy)
        self.ProgressTitle.setStyleSheet(u"QLabel {\n"
"	background-color: transparent;\n"
"}")
        self.ProgressTitle.setInputMethodHints(Qt.ImhNone)
        self.ProgressTitle.setTextFormat(Qt.MarkdownText)
        self.ProgressTitle.setPixmap(QPixmap(u":/Logo/ico/images/blessingAILogo.png"))
        self.ProgressTitle.setScaledContents(True)
        self.ProgressTitle.setAlignment(Qt.AlignCenter)
        self.ProgressTitle.setWordWrap(False)
        self.Title_Bg = QLabel(self.dropShadoFrame)
        self.Title_Bg.setObjectName(u"Title_Bg")
        self.Title_Bg.setEnabled(True)
        self.Title_Bg.setGeometry(QRect(0, -30, 841, 461))
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Title_Bg.sizePolicy().hasHeightForWidth())
        self.Title_Bg.setSizePolicy(sizePolicy1)
        self.Title_Bg.setStyleSheet(u"QLabel {\n"
"	background-color: transparent;\n"
"}")
        self.Title_Bg.setInputMethodHints(Qt.ImhNone)
        self.Title_Bg.setTextFormat(Qt.MarkdownText)
        self.Title_Bg.setPixmap(QPixmap(u":/Logo/ico/images/blessingAILogo_emptyfill.png"))
        self.Title_Bg.setScaledContents(True)
        self.Title_Bg.setAlignment(Qt.AlignCenter)
        self.Title_Bg.setWordWrap(False)
        self.loading_message = QLabel(self.dropShadoFrame)
        self.loading_message.setObjectName(u"loading_message")
        self.loading_message.setGeometry(QRect(225, 440, 391, 61))
        font1 = QFont()
        font1.setFamilies([u"Noto Sans"])
        font1.setPointSize(13)
        self.loading_message.setFont(font1)
        self.loading_message.setStyleSheet(u"QLabel {\n"
"	background-color: transparent;\n"
"}")
        self.loading_message.setAlignment(Qt.AlignCenter)
        self.percentage_text = QLabel(self.dropShadoFrame)
        self.percentage_text.setObjectName(u"percentage_text")
        self.percentage_text.setEnabled(True)
        self.percentage_text.setGeometry(QRect(360, 410, 111, 61))
        font2 = QFont()
        font2.setFamilies([u"Noto Sans"])
        font2.setPointSize(16)
        font2.setBold(True)
        self.percentage_text.setFont(font2)
        self.percentage_text.setStyleSheet(u"QLabel {\n"
"	background-color: transparent;\n"
"}")
        self.percentage_text.setAlignment(Qt.AlignCenter)
        self.percentage_text.raise_()
        self.ogTitle.raise_()
        self.Title_Bg.raise_()
        self.ProgressTitle.raise_()
        self.loading_message.raise_()

        self.verticalLayout.addWidget(self.dropShadoFrame)

        QSplashScreen.setCentralWidget(self.centralwidget)

        self.retranslateUi(QSplashScreen)

        QMetaObject.connectSlotsByName(QSplashScreen)
    # setupUi

    def retranslateUi(self, QSplashScreen):
        QSplashScreen.setWindowTitle(QCoreApplication.translate("QSplashScreen", u"Loading... Blessing-AI", None))
        self.ogTitle.setText(QCoreApplication.translate("QSplashScreen", u"blessing AI", None))
        self.loading_message.setText(QCoreApplication.translate("QSplashScreen", u"Loading [audio_device.py] module", None))
        self.percentage_text.setText(QCoreApplication.translate("QSplashScreen", u"52 %", None))
    # retranslateUi

