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
        Dialog.resize(823, 546)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.verticalLayoutWidget = QtGui.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.frame = DropAreaFrame(self.verticalLayoutWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(1)
        self.verticalLayout_2.setContentsMargins(1, 1, 1, 1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.items_tree = QtGui.QTreeWidget(self.frame)
        self.items_tree.setObjectName("items_tree")
        self.items_tree.headerItem().setText(0, "1")
        self.items_tree.header().setVisible(False)
        self.verticalLayout_2.addWidget(self.items_tree)
        self.verticalLayout.addWidget(self.frame)
        self.tabWidget = QtGui.QTabWidget(self.splitter)
        self.tabWidget.setObjectName("tabWidget")
        self.details_tab = QtGui.QWidget()
        self.details_tab.setObjectName("details_tab")
        self.tabWidget.addTab(self.details_tab, "")
        self.progress_tab = QtGui.QWidget()
        self.progress_tab.setObjectName("progress_tab")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.progress_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.treeWidget = QtGui.QTreeWidget(self.progress_tab)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.verticalLayout_4.addWidget(self.treeWidget)
        self.tabWidget.addTab(self.progress_tab, "")
        self.settings_tab = QtGui.QWidget()
        self.settings_tab.setObjectName("settings_tab")
        self.tabWidget.addTab(self.settings_tab, "")
        self.verticalLayout_3.addWidget(self.splitter)
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
        self.verticalLayout_3.addWidget(self.bottom_frame)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Shotgun Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Please choose items to publish", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.details_tab), QtGui.QApplication.translate("Dialog", "Details", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.progress_tab), QtGui.QApplication.translate("Dialog", "Progress", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settings_tab), QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.validate.setText(QtGui.QApplication.translate("Dialog", "Validate", None, QtGui.QApplication.UnicodeUTF8))
        self.publish.setText(QtGui.QApplication.translate("Dialog", "Publish", None, QtGui.QApplication.UnicodeUTF8))

from ..drop_area import DropAreaFrame
from . import resources_rc
