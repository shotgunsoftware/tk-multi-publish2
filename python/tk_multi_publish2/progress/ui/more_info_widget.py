# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'more_info_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_MoreInfoWidget(object):
    def setupUi(self, MoreInfoWidget):
        MoreInfoWidget.setObjectName("MoreInfoWidget")
        MoreInfoWidget.resize(373, 293)
        self.verticalLayout = QtGui.QVBoxLayout(MoreInfoWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pixmap_label = QtGui.QLabel(MoreInfoWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pixmap_label.sizePolicy().hasHeightForWidth())
        self.pixmap_label.setSizePolicy(sizePolicy)
        self.pixmap_label.setMinimumSize(QtCore.QSize(16, 16))
        self.pixmap_label.setMaximumSize(QtCore.QSize(16, 16))
        self.pixmap_label.setText("")
        self.pixmap_label.setObjectName("pixmap_label")
        self.horizontalLayout.addWidget(self.pixmap_label)
        self.message_label = QtGui.QLabel(MoreInfoWidget)
        self.message_label.setObjectName("message_label")
        self.horizontalLayout.addWidget(self.message_label)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 10)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.text_edit = QtGui.QTextEdit(MoreInfoWidget)
        self.text_edit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.text_edit.setReadOnly(True)
        self.text_edit.setObjectName("text_edit")
        self.verticalLayout.addWidget(self.text_edit)

        self.retranslateUi(MoreInfoWidget)
        QtCore.QMetaObject.connectSlotsByName(MoreInfoWidget)

    def retranslateUi(self, MoreInfoWidget):
        MoreInfoWidget.setWindowTitle(QtGui.QApplication.translate("MoreInfoWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.message_label.setText(QtGui.QApplication.translate("MoreInfoWidget", "More Info...", None, QtGui.QApplication.UnicodeUTF8))

