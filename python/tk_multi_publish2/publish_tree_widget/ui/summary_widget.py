# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'summary_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from tank.platform.qt import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from tank.platform.qt import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls


from  . import resources_rc

class Ui_SummaryWidget(object):
    def setupUi(self, SummaryWidget):
        if not SummaryWidget.objectName():
            SummaryWidget.setObjectName(u"SummaryWidget")
        SummaryWidget.resize(300, 45)
        SummaryWidget.setMinimumSize(QSize(0, 45))
        self.verticalLayout = QVBoxLayout(SummaryWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(SummaryWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.icon = QLabel(self.frame)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(32, 32))
        self.icon.setMaximumSize(QSize(30, 30))
        self.icon.setPixmap(QPixmap(u":/tk_multi_publish2/icon_256.png"))
        self.icon.setScaledContents(True)

        self.horizontalLayout.addWidget(self.icon)

        self.header = QLabel(self.frame)
        self.header.setObjectName(u"header")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.header)

        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(SummaryWidget)

        QMetaObject.connectSlotsByName(SummaryWidget)
    # setupUi

    def retranslateUi(self, SummaryWidget):
        SummaryWidget.setWindowTitle(QCoreApplication.translate("SummaryWidget", u"Form", None))
        self.icon.setText("")
        self.header.setText(QCoreApplication.translate("SummaryWidget", u"<big>Summary</big>", None))
    # retranslateUi
