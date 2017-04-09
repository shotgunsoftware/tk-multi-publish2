# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progress_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ProgressWidget(object):
    def setupUi(self, ProgressWidget):
        ProgressWidget.setObjectName("ProgressWidget")
        ProgressWidget.resize(488, 76)
        self.horizontalLayout = QtGui.QHBoxLayout(ProgressWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtGui.QFrame(ProgressWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.status_icon = QtGui.QLabel(self.frame)
        self.status_icon.setMinimumSize(QtCore.QSize(20, 20))
        self.status_icon.setMaximumSize(QtCore.QSize(20, 20))
        self.status_icon.setText("")
        self.status_icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/status_success.png"))
        self.status_icon.setScaledContents(True)
        self.status_icon.setObjectName("status_icon")
        self.horizontalLayout_8.addWidget(self.status_icon)
        self.message = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.message.sizePolicy().hasHeightForWidth())
        self.message.setSizePolicy(sizePolicy)
        self.message.setWordWrap(True)
        self.message.setObjectName("message")
        self.horizontalLayout_8.addWidget(self.message)
        self.details_toggle = QtGui.QToolButton(self.frame)
        self.details_toggle.setObjectName("details_toggle")
        self.horizontalLayout_8.addWidget(self.details_toggle)
        self.verticalLayout_8.addLayout(self.horizontalLayout_8)
        self.progress_bar = QtGui.QProgressBar(self.frame)
        self.progress_bar.setMaximumSize(QtCore.QSize(16777215, 10))
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout_8.addWidget(self.progress_bar)
        self.horizontalLayout.addWidget(self.frame)

        self.retranslateUi(ProgressWidget)
        QtCore.QMetaObject.connectSlotsByName(ProgressWidget)

    def retranslateUi(self, ProgressWidget):
        ProgressWidget.setWindowTitle(QtGui.QApplication.translate("ProgressWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.message.setText(QtGui.QApplication.translate("ProgressWidget", "Progress", None, QtGui.QApplication.UnicodeUTF8))
        self.details_toggle.setText(QtGui.QApplication.translate("ProgressWidget", "details", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
