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
        ContextWidget.resize(352, 81)
        ContextWidget.setMinimumSize(QtCore.QSize(0, 45))
        self.gridLayout = QtGui.QGridLayout(ContextWidget)
        self.gridLayout.setContentsMargins(4, 4, 4, 4)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.link_label = QtGui.QLabel(ContextWidget)
        self.link_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.link_label.setObjectName("link_label")
        self.gridLayout.addWidget(self.link_label, 0, 0, 1, 1)
        self.context_link = QtGui.QLineEdit(ContextWidget)
        self.context_link.setObjectName("context_link")
        self.gridLayout.addWidget(self.context_link, 0, 1, 1, 1)
        self.link_label_2 = QtGui.QLabel(ContextWidget)
        self.link_label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.link_label_2.setObjectName("link_label_2")
        self.gridLayout.addWidget(self.link_label_2, 1, 0, 1, 1)
        self.context_task = QtGui.QComboBox(ContextWidget)
        self.context_task.setObjectName("context_task")
        self.gridLayout.addWidget(self.context_task, 1, 1, 1, 1)

        self.retranslateUi(ContextWidget)
        QtCore.QMetaObject.connectSlotsByName(ContextWidget)

    def retranslateUi(self, ContextWidget):
        ContextWidget.setWindowTitle(QtGui.QApplication.translate("ContextWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.link_label.setText(QtGui.QApplication.translate("ContextWidget", "Shotgun Link", None, QtGui.QApplication.UnicodeUTF8))
        self.link_label_2.setText(QtGui.QApplication.translate("ContextWidget", "Associated Task", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
