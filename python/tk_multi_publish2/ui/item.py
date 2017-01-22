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
        Item.resize(346, 81)
        self.gridLayout = QtGui.QGridLayout(Item)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.item_icon = QtGui.QLabel(Item)
        self.item_icon.setMinimumSize(QtCore.QSize(38, 32))
        self.item_icon.setMaximumSize(QtCore.QSize(38, 32))
        self.item_icon.setText("")
        self.item_icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/item.png"))
        self.item_icon.setScaledContents(True)
        self.item_icon.setObjectName("item_icon")
        self.horizontalLayout_3.addWidget(self.item_icon)
        self.header = QtGui.QLabel(Item)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setObjectName("header")
        self.horizontalLayout_3.addWidget(self.header)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.header_chk = QtGui.QCheckBox(Item)
        self.header_chk.setText("")
        self.header_chk.setObjectName("header_chk")
        self.gridLayout.addWidget(self.header_chk, 0, 1, 1, 1)
        self.hidden_header = QtGui.QLabel(Item)
        self.hidden_header.setObjectName("hidden_header")
        self.gridLayout.addWidget(self.hidden_header, 1, 0, 1, 1)

        self.retranslateUi(Item)
        QtCore.QMetaObject.connectSlotsByName(Item)

    def retranslateUi(self, Item):
        Item.setWindowTitle(QtGui.QApplication.translate("Item", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("Item", "<big>Alembic Caches</big><br>\n"
"Publish Alembic Caches", None, QtGui.QApplication.UnicodeUTF8))
        self.hidden_header.setText(QtGui.QApplication.translate("Item", "Hidden header", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
