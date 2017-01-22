# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(932, 609)
        Dialog.setStyleSheet("")
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.left_header_label = QtGui.QLabel(Dialog)
        self.left_header_label.setObjectName("left_header_label")
        self.verticalLayout.addWidget(self.left_header_label)
        self.plugin_selector = PluginSelector(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plugin_selector.sizePolicy().hasHeightForWidth())
        self.plugin_selector.setSizePolicy(sizePolicy)
        self.plugin_selector.setObjectName("plugin_selector")
        self.verticalLayout.addWidget(self.plugin_selector)
        self.bottom_frame = QtGui.QFrame(Dialog)
        self.bottom_frame.setMaximumSize(QtCore.QSize(16777215, 40))
        self.bottom_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.bottom_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.bottom_frame.setObjectName("bottom_frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.bottom_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.reload = QtGui.QPushButton(self.bottom_frame)
        self.reload.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/reload.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reload.setIcon(icon)
        self.reload.setObjectName("reload")
        self.horizontalLayout.addWidget(self.reload)
        self.validate = QtGui.QPushButton(self.bottom_frame)
        self.validate.setObjectName("validate")
        self.horizontalLayout.addWidget(self.validate)
        spacerItem = QtGui.QSpacerItem(638, 11, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.publish = QtGui.QPushButton(self.bottom_frame)
        self.publish.setObjectName("publish")
        self.horizontalLayout.addWidget(self.publish)
        self.verticalLayout.addWidget(self.bottom_frame)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Shotgun Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.left_header_label.setText(QtGui.QApplication.translate("Dialog", "Items to be processed", None, QtGui.QApplication.UnicodeUTF8))
        self.validate.setText(QtGui.QApplication.translate("Dialog", "Validate", None, QtGui.QApplication.UnicodeUTF8))
        self.publish.setText(QtGui.QApplication.translate("Dialog", "Publish", None, QtGui.QApplication.UnicodeUTF8))

from ..plugin_selector import PluginSelector
from . import resources_rc
