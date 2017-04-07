# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'task_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_TaskWidget(object):
    def setupUi(self, TaskWidget):
        TaskWidget.setObjectName("TaskWidget")
        TaskWidget.resize(331, 34)
        self.horizontalLayout = QtGui.QHBoxLayout(TaskWidget)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkbox = QtGui.QCheckBox(TaskWidget)
        self.checkbox.setText("")
        self.checkbox.setObjectName("checkbox")
        self.horizontalLayout.addWidget(self.checkbox)
        self.icon = QtGui.QLabel(TaskWidget)
        self.icon.setMinimumSize(QtCore.QSize(26, 26))
        self.icon.setMaximumSize(QtCore.QSize(26, 26))
        self.icon.setText("")
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.header = QtGui.QLabel(TaskWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setObjectName("header")
        self.horizontalLayout.addWidget(self.header)
        self.status = StatusDotWidget(TaskWidget)
        self.status.setObjectName("status")
        self.horizontalLayout.addWidget(self.status)
        self.settings = QtGui.QToolButton(TaskWidget)
        self.settings.setObjectName("settings")
        self.horizontalLayout.addWidget(self.settings)

        self.retranslateUi(TaskWidget)
        QtCore.QMetaObject.connectSlotsByName(TaskWidget)

    def retranslateUi(self, TaskWidget):
        TaskWidget.setWindowTitle(QtGui.QApplication.translate("TaskWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("TaskWidget", "<big>Alembic Caches</big>", None, QtGui.QApplication.UnicodeUTF8))
        self.settings.setText(QtGui.QApplication.translate("TaskWidget", "...", None, QtGui.QApplication.UnicodeUTF8))

from ..status_dot_widget import StatusDotWidget
from . import resources_rc
