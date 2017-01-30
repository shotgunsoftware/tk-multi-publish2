# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'item.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Item(object):
    def setupUi(self, Item):
        Item.setObjectName("Item")
        Item.resize(288, 30)
        self.horizontalLayout = QtGui.QHBoxLayout(Item)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.stack = QtGui.QStackedWidget(Item)
        self.stack.setMaximumSize(QtCore.QSize(20, 20))
        self.stack.setObjectName("stack")
        self.widget_2 = QtGui.QWidget()
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout = QtGui.QVBoxLayout(self.widget_2)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.status = ItemStatus(self.widget_2)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.stack.addWidget(self.widget_2)
        self.chk_page = QtGui.QWidget()
        self.chk_page.setObjectName("chk_page")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.chk_page)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.checkbox = QtGui.QCheckBox(self.chk_page)
        self.checkbox.setText("")
        self.checkbox.setTristate(True)
        self.checkbox.setObjectName("checkbox")
        self.verticalLayout_2.addWidget(self.checkbox)
        self.stack.addWidget(self.chk_page)
        self.horizontalLayout.addWidget(self.stack)
        self.icon = QtGui.QLabel(Item)
        self.icon.setMinimumSize(QtCore.QSize(30, 30))
        self.icon.setMaximumSize(QtCore.QSize(30, 30))
        self.icon.setText("")
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.header = QtGui.QLabel(Item)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setObjectName("header")
        self.horizontalLayout.addWidget(self.header)

        self.retranslateUi(Item)
        self.stack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Item)

    def retranslateUi(self, Item):
        Item.setWindowTitle(QtGui.QApplication.translate("Item", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("Item", "<big>Alembic Caches</big>", None, QtGui.QApplication.UnicodeUTF8))

from ..item_status import ItemStatus
from . import resources_rc
