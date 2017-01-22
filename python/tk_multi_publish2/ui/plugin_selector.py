# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plugin_selector.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_PluginSelector(object):
    def setupUi(self, PluginSelector):
        PluginSelector.setObjectName("PluginSelector")
        PluginSelector.resize(494, 322)
        PluginSelector.setStyleSheet("")
        self.horizontalLayout = QtGui.QHBoxLayout(PluginSelector)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.left_scroll = QtGui.QScrollArea(PluginSelector)
        self.left_scroll.setWidgetResizable(True)
        self.left_scroll.setObjectName("left_scroll")
        self.left_scroll_contents = QtGui.QWidget()
        self.left_scroll_contents.setGeometry(QtCore.QRect(0, 0, 245, 320))
        self.left_scroll_contents.setObjectName("left_scroll_contents")
        self.left_scroll_layout = QtGui.QVBoxLayout(self.left_scroll_contents)
        self.left_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.left_scroll_layout.setObjectName("left_scroll_layout")
        self.left_scroll.setWidget(self.left_scroll_contents)
        self.horizontalLayout.addWidget(self.left_scroll)
        self.details_stack = QtGui.QStackedWidget(PluginSelector)
        self.details_stack.setStyleSheet("")
        self.details_stack.setObjectName("details_stack")
        self.horizontalLayout.addWidget(self.details_stack)

        self.retranslateUi(PluginSelector)
        self.details_stack.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(PluginSelector)

    def retranslateUi(self, PluginSelector):
        PluginSelector.setWindowTitle(QtGui.QApplication.translate("PluginSelector", "Shotgun Publish", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
