# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'summary_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_SummaryWidget(object):
    def setupUi(self, SummaryWidget):
        SummaryWidget.setObjectName("SummaryWidget")
        SummaryWidget.resize(300, 45)
        SummaryWidget.setMinimumSize(QtCore.QSize(0, 45))
        self.verticalLayout = QtGui.QVBoxLayout(SummaryWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtGui.QFrame(SummaryWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon = QtGui.QLabel(self.frame)
        self.icon.setMinimumSize(QtCore.QSize(32, 32))
        self.icon.setMaximumSize(QtCore.QSize(30, 30))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/icon_256.png"))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.header = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setObjectName("header")
        self.horizontalLayout.addWidget(self.header)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(SummaryWidget)
        QtCore.QMetaObject.connectSlotsByName(SummaryWidget)

    def retranslateUi(self, SummaryWidget):
        SummaryWidget.setWindowTitle(QtGui.QApplication.translate("SummaryWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("SummaryWidget", "<big>Summary</big>", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
