# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_SettingsWidget(object):
    def setupUi(self, SettingsWidget):
        SettingsWidget.setObjectName("SettingsWidget")
        SettingsWidget.resize(337, 645)
        self.verticalLayout = QtGui.QVBoxLayout(SettingsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.settings_scroll_area = QtGui.QScrollArea(SettingsWidget)
        self.settings_scroll_area.setWidgetResizable(True)
        self.settings_scroll_area.setObjectName("settings_scroll_area")
        self.settings_host = QtGui.QWidget()
        self.settings_host.setGeometry(QtCore.QRect(0, 0, 335, 643))
        self.settings_host.setObjectName("settings_host")
        self.settings_layout = QtGui.QGridLayout(self.settings_host)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setSpacing(0)
        self.settings_layout.setObjectName("settings_layout")
        self.settings_scroll_area.setWidget(self.settings_host)
        self.verticalLayout.addWidget(self.settings_scroll_area)

        self.retranslateUi(SettingsWidget)
        QtCore.QMetaObject.connectSlotsByName(SettingsWidget)

    def retranslateUi(self, SettingsWidget):
        SettingsWidget.setWindowTitle(QtGui.QApplication.translate("SettingsWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

