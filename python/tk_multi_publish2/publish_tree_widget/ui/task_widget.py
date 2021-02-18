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
        TaskWidget.resize(338, 36)
        self.verticalLayout = QtGui.QVBoxLayout(TaskWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtGui.QFrame(TaskWidget)
        self.frame.setMinimumSize(QtCore.QSize(0, 32))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setContentsMargins(8, 2, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon = QtGui.QLabel(self.frame)
        self.icon.setMinimumSize(QtCore.QSize(18, 18))
        self.icon.setMaximumSize(QtCore.QSize(18, 18))
        self.icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/shotgun.png"))
        self.icon.setScaledContents(True)
        self.icon.setAlignment(QtCore.Qt.AlignCenter)
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.header = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setMinimumSize(QtCore.QSize(1, 1))
        self.header.setAccessibleName("")
        self.header.setObjectName("header")
        self.horizontalLayout.addWidget(self.header)
        self.status = QtGui.QToolButton(self.frame)
        self.status.setMinimumSize(QtCore.QSize(30, 22))
        self.status.setMaximumSize(QtCore.QSize(30, 22))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/status_publish.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.status.setIcon(icon)
        self.status.setIconSize(QtCore.QSize(16, 16))
        self.status.setObjectName("status")
        self.horizontalLayout.addWidget(self.status)
        self.checkbox = QtGui.QCheckBox(self.frame)
        self.checkbox.setObjectName("checkbox")
        self.horizontalLayout.addWidget(self.checkbox)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(TaskWidget)
        QtCore.QMetaObject.connectSlotsByName(TaskWidget)

    def retranslateUi(self, TaskWidget):
        TaskWidget.setWindowTitle(QtGui.QApplication.translate("TaskWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        TaskWidget.setAccessibleName(QtGui.QApplication.translate("TaskWidget", "task widget", None, QtGui.QApplication.UnicodeUTF8))
        self.frame.setAccessibleName(QtGui.QApplication.translate("TaskWidget", "task widget inner frame", None, QtGui.QApplication.UnicodeUTF8))
        self.icon.setAccessibleName(QtGui.QApplication.translate("TaskWidget", "task icon", None, QtGui.QApplication.UnicodeUTF8))
        self.header.setText(QtGui.QApplication.translate("TaskWidget", "<big>Alembic Caches</big>", None, QtGui.QApplication.UnicodeUTF8))
        self.status.setToolTip(QtGui.QApplication.translate("TaskWidget", "Click for more details", None, QtGui.QApplication.UnicodeUTF8))
        self.status.setAccessibleName(QtGui.QApplication.translate("TaskWidget", "task status", None, QtGui.QApplication.UnicodeUTF8))
        self.status.setText(QtGui.QApplication.translate("TaskWidget", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.checkbox.setToolTip(QtGui.QApplication.translate("TaskWidget", "hint: shift-click to toggle all items of this type", None, QtGui.QApplication.UnicodeUTF8))
        self.checkbox.setAccessibleName(QtGui.QApplication.translate("TaskWidget", "task checkbox", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
