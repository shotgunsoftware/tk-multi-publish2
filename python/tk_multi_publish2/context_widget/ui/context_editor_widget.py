# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'context_editor_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ContextWidget(object):
    def setupUi(self, ContextWidget):
        ContextWidget.setObjectName("ContextWidget")
        ContextWidget.resize(300, 60)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ContextWidget.sizePolicy().hasHeightForWidth())
        ContextWidget.setSizePolicy(sizePolicy)
        ContextWidget.setMinimumSize(QtCore.QSize(0, 60))
        self.verticalLayout = QtGui.QVBoxLayout(ContextWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(ContextWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.context_layout = QtGui.QHBoxLayout()
        self.context_layout.setObjectName("context_layout")
        self.link_placeholder = QtGui.QLabel(ContextWidget)
        self.link_placeholder.setObjectName("link_placeholder")
        self.context_layout.addWidget(self.link_placeholder)
        self.task_placeholder = QtGui.QLabel(ContextWidget)
        self.task_placeholder.setObjectName("task_placeholder")
        self.context_layout.addWidget(self.task_placeholder)
        self.verticalLayout.addLayout(self.context_layout)
        spacerItem = QtGui.QSpacerItem(13, 11, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ContextWidget)
        QtCore.QMetaObject.connectSlotsByName(ContextWidget)

    def retranslateUi(self, ContextWidget):
        ContextWidget.setWindowTitle(QtGui.QApplication.translate("ContextWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ContextWidget", "Link this item to a Shotgun entity and task:", None, QtGui.QApplication.UnicodeUTF8))
        self.link_placeholder.setText(QtGui.QApplication.translate("ContextWidget", "Loading...", None, QtGui.QApplication.UnicodeUTF8))
        self.task_placeholder.setText(QtGui.QApplication.translate("ContextWidget", "Loading...", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
