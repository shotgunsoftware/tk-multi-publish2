# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'context_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ContextWidget(object):
    def setupUi(self, ContextWidget):
        ContextWidget.setObjectName("ContextWidget")
        ContextWidget.resize(252, 16)
        self.verticalLayout = QtGui.QVBoxLayout(ContextWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtGui.QFrame(ContextWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.header = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setObjectName("header")
        self.horizontalLayout.addWidget(self.header)
        self.checkbox = QtGui.QCheckBox(self.frame)
        self.checkbox.setObjectName("checkbox")
        self.horizontalLayout.addWidget(self.checkbox)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(ContextWidget)
        QtCore.QMetaObject.connectSlotsByName(ContextWidget)

    def retranslateUi(self, ContextWidget):
        ContextWidget.setWindowTitle(QtGui.QApplication.translate("ContextWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("ContextWidget", "context", None, QtGui.QApplication.UnicodeUTF8))
        self.checkbox.setToolTip(QtGui.QApplication.translate("ContextWidget", "hint: shift-click to toggle all items of this type", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
