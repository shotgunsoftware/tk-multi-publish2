# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'summary_overlay.ui'
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


from ..progress_status_label import ProgressStatusLabel

from  . import resources_rc

class Ui_SummaryOverlay(object):
    def setupUi(self, SummaryOverlay):
        if not SummaryOverlay.objectName():
            SummaryOverlay.setObjectName(u"SummaryOverlay")
        SummaryOverlay.resize(551, 365)
        SummaryOverlay.setAutoFillBackground(True)
        self.verticalLayout = QVBoxLayout(SummaryOverlay)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.summary_frame = QFrame(SummaryOverlay)
        self.summary_frame.setObjectName(u"summary_frame")
        self.summary_frame.setAutoFillBackground(False)
        self.summary_frame.setFrameShape(QFrame.StyledPanel)
        self.summary_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.summary_frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_2 = QSpacerItem(20, 46, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.horizontalSpacer = QSpacerItem(126, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.icon = QLabel(self.summary_frame)
        self.icon.setObjectName(u"icon")
        self.icon.setMaximumSize(QSize(80, 80))
        self.icon.setPixmap(QPixmap(u":/tk_multi_publish2/publish_complete.png"))
        self.icon.setScaledContents(True)

        self.horizontalLayout.addWidget(self.icon)

        self.label = QLabel(self.summary_frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.info = ProgressStatusLabel(self.summary_frame)
        self.info.setObjectName(u"info")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy)
        self.info.setScaledContents(True)
        self.info.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.info.setWordWrap(True)

        self.horizontalLayout_3.addWidget(self.info)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 10)
        self.horizontalLayout_3.setStretch(2, 1)

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_6)

        self.publish_again = ProgressStatusLabel(self.summary_frame)
        self.publish_again.setObjectName(u"publish_again")

        self.horizontalLayout_4.addWidget(self.publish_again)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 10)
        self.horizontalLayout_4.setStretch(2, 1)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.verticalSpacer_3 = QSpacerItem(20, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.verticalLayout_3.setStretch(3, 100)

        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalSpacer_2 = QSpacerItem(125, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_2.setStretch(0, 4)
        self.horizontalLayout_2.setStretch(1, 5)
        self.horizontalLayout_2.setStretch(2, 3)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 46, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1, 1, 1)

        self.verticalLayout.addWidget(self.summary_frame)

        self.retranslateUi(SummaryOverlay)

        QMetaObject.connectSlotsByName(SummaryOverlay)
    # setupUi

    def retranslateUi(self, SummaryOverlay):
        SummaryOverlay.setWindowTitle(QCoreApplication.translate("SummaryOverlay", u"Form", None))
        self.icon.setText("")
        self.label.setText(QCoreApplication.translate("SummaryOverlay", u"TextLabel", None))
        self.info.setText(QCoreApplication.translate("SummaryOverlay", u"TextLabel", None))
        self.publish_again.setText(QCoreApplication.translate("SummaryOverlay", u"TextLabel", None))
    # retranslateUi
