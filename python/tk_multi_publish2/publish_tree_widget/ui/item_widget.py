# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'item_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ItemWidget(object):
    def setupUi(self, ItemWidget):
        ItemWidget.setObjectName("ItemWidget")
        ItemWidget.resize(415, 53)
        self.horizontalLayout = QtGui.QHBoxLayout(ItemWidget)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkbox = QtGui.QCheckBox(ItemWidget)
        self.checkbox.setText("")
        self.checkbox.setObjectName("checkbox")
        self.horizontalLayout.addWidget(self.checkbox)
        self.icon = QtGui.QLabel(ItemWidget)
        self.icon.setMinimumSize(QtCore.QSize(26, 26))
        self.icon.setMaximumSize(QtCore.QSize(26, 26))
        self.icon.setText("")
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.header = QtGui.QLabel(ItemWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setObjectName("header")
        self.horizontalLayout.addWidget(self.header)
        self.status = StatusDotWidget(ItemWidget)
        self.status.setObjectName("status")
        self.horizontalLayout.addWidget(self.status)

        self.retranslateUi(ItemWidget)
        QtCore.QMetaObject.connectSlotsByName(ItemWidget)

    def retranslateUi(self, ItemWidget):
        ItemWidget.setWindowTitle(QtGui.QApplication.translate("ItemWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("ItemWidget", "<big>Alembic Caches</big><br>foo", None, QtGui.QApplication.UnicodeUTF8))

from ..status_dot_widget import StatusDotWidget
from . import resources_rc
