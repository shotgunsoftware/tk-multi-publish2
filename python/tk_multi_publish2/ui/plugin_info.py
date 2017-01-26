# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plugin_info.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_PluginInfo(object):
    def setupUi(self, PluginInfo):
        PluginInfo.setObjectName("PluginInfo")
        PluginInfo.resize(294, 129)
        self.verticalLayout_2 = QtGui.QVBoxLayout(PluginInfo)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon = QtGui.QLabel(PluginInfo)
        self.icon.setMinimumSize(QtCore.QSize(50, 50))
        self.icon.setMaximumSize(QtCore.QSize(50, 50))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/item.png"))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.name = QtGui.QLabel(PluginInfo)
        self.name.setWordWrap(True)
        self.name.setObjectName("name")
        self.verticalLayout.addWidget(self.name)
        self.description = QtGui.QLabel(PluginInfo)
        self.description.setTextFormat(QtCore.Qt.RichText)
        self.description.setWordWrap(True)
        self.description.setObjectName("description")
        self.verticalLayout.addWidget(self.description)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.options_header = QtGui.QLabel(PluginInfo)
        self.options_header.setWordWrap(True)
        self.options_header.setObjectName("options_header")
        self.verticalLayout_2.addWidget(self.options_header)
        self.settings_layout = QtGui.QVBoxLayout()
        self.settings_layout.setObjectName("settings_layout")
        self.verticalLayout_2.addLayout(self.settings_layout)

        self.retranslateUi(PluginInfo)
        QtCore.QMetaObject.connectSlotsByName(PluginInfo)

    def retranslateUi(self, PluginInfo):
        PluginInfo.setWindowTitle(QtGui.QApplication.translate("PluginInfo", "Details", None, QtGui.QApplication.UnicodeUTF8))
        self.name.setText(QtGui.QApplication.translate("PluginInfo", "Plugin Name", None, QtGui.QApplication.UnicodeUTF8))
        self.description.setText(QtGui.QApplication.translate("PluginInfo", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.options_header.setText(QtGui.QApplication.translate("PluginInfo", "Options", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
