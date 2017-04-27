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
        ItemWidget.resize(337, 48)
        ItemWidget.setMinimumSize(QtCore.QSize(0, 45))
        self.verticalLayout = QtGui.QVBoxLayout(ItemWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtGui.QFrame(ItemWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.drag_handle = QtGui.QLabel(self.frame)
        self.drag_handle.setMinimumSize(QtCore.QSize(16, 16))
        self.drag_handle.setMaximumSize(QtCore.QSize(16, 16))
        self.drag_handle.setCursor(QtCore.Qt.OpenHandCursor)
        self.drag_handle.setText("")
        self.drag_handle.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/drag_handle.png"))
        self.drag_handle.setScaledContents(True)
        self.drag_handle.setObjectName("drag_handle")
        self.horizontalLayout.addWidget(self.drag_handle)
        self.icon = QtGui.QLabel(self.frame)
        self.icon.setMinimumSize(QtCore.QSize(32, 32))
        self.icon.setMaximumSize(QtCore.QSize(30, 30))
        self.icon.setText("")
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
        self.status = QtGui.QToolButton(self.frame)
        self.status.setMinimumSize(QtCore.QSize(30, 30))
        self.status.setMaximumSize(QtCore.QSize(30, 30))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/status_validate.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.status.setIcon(icon)
        self.status.setIconSize(QtCore.QSize(24, 24))
        self.status.setObjectName("status")
        self.horizontalLayout.addWidget(self.status)
        self.checkbox = QtGui.QCheckBox(self.frame)
        self.checkbox.setText("")
        self.checkbox.setObjectName("checkbox")
        self.horizontalLayout.addWidget(self.checkbox)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(ItemWidget)
        QtCore.QMetaObject.connectSlotsByName(ItemWidget)

    def retranslateUi(self, ItemWidget):
        ItemWidget.setWindowTitle(QtGui.QApplication.translate("ItemWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("ItemWidget", "<big>Alembic Caches</big><br>foo", None, QtGui.QApplication.UnicodeUTF8))
        self.status.setToolTip(QtGui.QApplication.translate("ItemWidget", "Click for details", None, QtGui.QApplication.UnicodeUTF8))
        self.status.setText(QtGui.QApplication.translate("ItemWidget", "...", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
