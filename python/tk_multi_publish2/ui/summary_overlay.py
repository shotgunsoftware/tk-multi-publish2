# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'summary_overlay.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_SummaryOverlay(object):
    def setupUi(self, SummaryOverlay):
        SummaryOverlay.setObjectName("SummaryOverlay")
        SummaryOverlay.resize(551, 365)
        SummaryOverlay.setAutoFillBackground(True)
        self.verticalLayout = QtGui.QVBoxLayout(SummaryOverlay)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.summary_frame = QtGui.QFrame(SummaryOverlay)
        self.summary_frame.setAutoFillBackground(False)
        self.summary_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.summary_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.summary_frame.setObjectName("summary_frame")
        self.gridLayout = QtGui.QGridLayout(self.summary_frame)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtGui.QSpacerItem(125, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(126, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon = QtGui.QLabel(self.summary_frame)
        self.icon.setMaximumSize(QtCore.QSize(80, 80))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/publish_complete.png"))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.label = QtGui.QLabel(self.summary_frame)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 46, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 3, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 46, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 0, 1, 1, 1)
        self.details = ProgressStatusLabel(self.summary_frame)
        self.details.setObjectName("details")
        self.gridLayout.addWidget(self.details, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.summary_frame)

        self.retranslateUi(SummaryOverlay)
        QtCore.QMetaObject.connectSlotsByName(SummaryOverlay)

    def retranslateUi(self, SummaryOverlay):
        SummaryOverlay.setWindowTitle(QtGui.QApplication.translate("SummaryOverlay", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SummaryOverlay", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.details.setText(QtGui.QApplication.translate("SummaryOverlay", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

from ..progress_status_label import ProgressStatusLabel
from . import resources_rc
