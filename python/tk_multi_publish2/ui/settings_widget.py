# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from tank.platform.qt import QtCore
for name, cls in QtCore.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls

from tank.platform.qt import QtGui
for name, cls in QtGui.__dict__.items():
    if isinstance(cls, type): globals()[name] = cls


class Ui_SettingsWidget(object):
    def setupUi(self, SettingsWidget):
        if not SettingsWidget.objectName():
            SettingsWidget.setObjectName(u"SettingsWidget")
        SettingsWidget.resize(337, 645)
        self.verticalLayout = QVBoxLayout(SettingsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.settings_scroll_area = QScrollArea(SettingsWidget)
        self.settings_scroll_area.setObjectName(u"settings_scroll_area")
        self.settings_scroll_area.setWidgetResizable(True)
        self.settings_host = QWidget()
        self.settings_host.setObjectName(u"settings_host")
        self.settings_host.setGeometry(QRect(0, 0, 335, 643))
        self.settings_layout = QGridLayout(self.settings_host)
        self.settings_layout.setSpacing(0)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setObjectName(u"settings_layout")
        self.settings_scroll_area.setWidget(self.settings_host)

        self.verticalLayout.addWidget(self.settings_scroll_area)

        self.retranslateUi(SettingsWidget)

        QMetaObject.connectSlotsByName(SettingsWidget)
    # setupUi

    def retranslateUi(self, SettingsWidget):
        SettingsWidget.setWindowTitle(QCoreApplication.translate("SettingsWidget", u"Form", None))
    # retranslateUi
