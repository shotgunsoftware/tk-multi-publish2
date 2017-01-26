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
        Item.resize(319, 54)
        self.horizontalLayout = QtGui.QHBoxLayout(Item)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.left_stack = QtGui.QStackedWidget(Item)
        self.left_stack.setMaximumSize(QtCore.QSize(20, 20))
        self.left_stack.setObjectName("left_stack")
        self.widget_2 = QtGui.QWidget()
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout = QtGui.QVBoxLayout(self.widget_2)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = PublishStatus(self.widget_2)
        self.widget.setObjectName("widget")
        self.verticalLayout.addWidget(self.widget)
        self.left_stack.addWidget(self.widget_2)
        self.chk_page = QtGui.QWidget()
        self.chk_page.setObjectName("chk_page")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.chk_page)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.item_chk = QtGui.QCheckBox(self.chk_page)
        self.item_chk.setText("")
        self.item_chk.setTristate(True)
        self.item_chk.setObjectName("item_chk")
        self.verticalLayout_2.addWidget(self.item_chk)
        self.left_stack.addWidget(self.chk_page)
        self.horizontalLayout.addWidget(self.left_stack)
        self.icon = ItemIcon(Item)
        self.icon.setMinimumSize(QtCore.QSize(80, 45))
        self.icon.setMaximumSize(QtCore.QSize(80, 45))
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
        self.left_stack.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Item)

    def retranslateUi(self, Item):
        Item.setWindowTitle(QtGui.QApplication.translate("Item", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("Item", "<big>Alembic Caches</big>", None, QtGui.QApplication.UnicodeUTF8))

from ..item_icon import ItemIcon
from ..publish_status import PublishStatus
from . import resources_rc
