# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'details.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Details(object):
    def setupUi(self, Details):
        Details.setObjectName("Details")
        Details.resize(372, 452)
        self.verticalLayout = QtGui.QVBoxLayout(Details)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.details_scroll = QtGui.QScrollArea(Details)
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setObjectName("details_scroll")
        self.scrollAreaWidgetContents_2 = QtGui.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 370, 450))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.details_frame = QtGui.QFrame(self.scrollAreaWidgetContents_2)
        self.details_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.details_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.details_frame.setObjectName("details_frame")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.details_frame)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.information_header = QtGui.QLabel(self.details_frame)
        self.information_header.setWordWrap(True)
        self.information_header.setObjectName("information_header")
        self.verticalLayout_4.addWidget(self.information_header)
        self.information = QtGui.QLabel(self.details_frame)
        self.information.setTextFormat(QtCore.Qt.RichText)
        self.information.setWordWrap(True)
        self.information.setObjectName("information")
        self.verticalLayout_4.addWidget(self.information)
        self.options_header = QtGui.QLabel(self.details_frame)
        self.options_header.setWordWrap(True)
        self.options_header.setObjectName("options_header")
        self.verticalLayout_4.addWidget(self.options_header)
        self.settings_layout = QtGui.QVBoxLayout()
        self.settings_layout.setObjectName("settings_layout")
        self.verticalLayout_4.addLayout(self.settings_layout)
        self.status_header = QtGui.QLabel(self.details_frame)
        self.status_header.setWordWrap(True)
        self.status_header.setObjectName("status_header")
        self.verticalLayout_4.addWidget(self.status_header)
        self.log_list = QtGui.QListWidget(self.details_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.log_list.sizePolicy().hasHeightForWidth())
        self.log_list.setSizePolicy(sizePolicy)
        self.log_list.setAlternatingRowColors(True)
        self.log_list.setProperty("isWrapping", False)
        self.log_list.setWordWrap(True)
        self.log_list.setObjectName("log_list")
        self.verticalLayout_4.addWidget(self.log_list)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.verticalLayout_2.addWidget(self.details_frame)
        self.details_scroll.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout.addWidget(self.details_scroll)

        self.retranslateUi(Details)
        QtCore.QMetaObject.connectSlotsByName(Details)

    def retranslateUi(self, Details):
        Details.setWindowTitle(QtGui.QApplication.translate("Details", "Details", None, QtGui.QApplication.UnicodeUTF8))
        self.information_header.setText(QtGui.QApplication.translate("Details", "Information", None, QtGui.QApplication.UnicodeUTF8))
        self.information.setText(QtGui.QApplication.translate("Details", "details about the publish task", None, QtGui.QApplication.UnicodeUTF8))
        self.options_header.setText(QtGui.QApplication.translate("Details", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.status_header.setText(QtGui.QApplication.translate("Details", "Status", None, QtGui.QApplication.UnicodeUTF8))

