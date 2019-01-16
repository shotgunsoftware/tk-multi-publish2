# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progress_details_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ProgressDetailsWidget(object):
    def setupUi(self, ProgressDetailsWidget):
        ProgressDetailsWidget.setObjectName("ProgressDetailsWidget")
        ProgressDetailsWidget.resize(370, 233)
        self.verticalLayout = QtGui.QVBoxLayout(ProgressDetailsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.progress_frame = QtGui.QFrame(ProgressDetailsWidget)
        self.progress_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.progress_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.progress_frame.setObjectName("progress_frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.progress_frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.progress_label = QtGui.QLabel(self.progress_frame)
        self.progress_label.setObjectName("progress_label")
        self.horizontalLayout.addWidget(self.progress_label)
        self.copy_log_button = QtGui.QToolButton(self.progress_frame)
        self.copy_log_button.setMinimumSize(QtCore.QSize(105, 0))
        self.copy_log_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.copy_log_button.setObjectName("copy_log_button")
        self.horizontalLayout.addWidget(self.copy_log_button)
        self.close = QtGui.QToolButton(self.progress_frame)
        self.close.setMinimumSize(QtCore.QSize(30, 30))
        self.close.setMaximumSize(QtCore.QSize(30, 30))
        self.close.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/cross.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.close.setIcon(icon)
        self.close.setIconSize(QtCore.QSize(30, 30))
        self.close.setObjectName("close")
        self.horizontalLayout.addWidget(self.close)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.log_tree = QtGui.QTreeWidget(self.progress_frame)
        self.log_tree.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerItem)
        self.log_tree.setUniformRowHeights(True)
        self.log_tree.setWordWrap(True)
        self.log_tree.setColumnCount(2)
        self.log_tree.setObjectName("log_tree")
        self.log_tree.headerItem().setText(0, "1")
        self.log_tree.headerItem().setText(1, "2")
        self.log_tree.header().setVisible(False)
        self.log_tree.header().setStretchLastSection(False)
        self.verticalLayout_2.addWidget(self.log_tree)
        self.verticalLayout.addWidget(self.progress_frame)

        self.retranslateUi(ProgressDetailsWidget)
        QtCore.QMetaObject.connectSlotsByName(ProgressDetailsWidget)

    def retranslateUi(self, ProgressDetailsWidget):
        ProgressDetailsWidget.setWindowTitle(QtGui.QApplication.translate("ProgressDetailsWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.progress_label.setText(QtGui.QApplication.translate("ProgressDetailsWidget", "Progress Details", None, QtGui.QApplication.UnicodeUTF8))
        self.copy_log_button.setToolTip(QtGui.QApplication.translate("ProgressDetailsWidget", "<html><head/><body><p>Open the publisher\'s log file. The log file is useful for deeper debugging of publish issues. For issues involving Shotgun Support, please include a copy of this file when submitting a support request. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.copy_log_button.setText(QtGui.QApplication.translate("ProgressDetailsWidget", "Copy to Clipboard", None, QtGui.QApplication.UnicodeUTF8))
        self.close.setToolTip(QtGui.QApplication.translate("ProgressDetailsWidget", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.log_tree.setAccessibleName(QtGui.QApplication.translate("ProgressDetailsWidget", "<html><head/><body><p>Opens the log file for the current engine which will include log messages from the publisher. This file is extremely useful for deeper debugging and understanding of publish issues. A copy of this file should be included when submitting support requests to the Shotgun Support team.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
