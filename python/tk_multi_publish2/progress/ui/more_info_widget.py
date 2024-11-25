# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'more_info_widget.ui'
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


class Ui_MoreInfoWidget(object):
    def setupUi(self, MoreInfoWidget):
        if not MoreInfoWidget.objectName():
            MoreInfoWidget.setObjectName(u"MoreInfoWidget")
        MoreInfoWidget.resize(373, 293)
        self.verticalLayout = QVBoxLayout(MoreInfoWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pixmap_label = QLabel(MoreInfoWidget)
        self.pixmap_label.setObjectName(u"pixmap_label")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pixmap_label.sizePolicy().hasHeightForWidth())
        self.pixmap_label.setSizePolicy(sizePolicy)
        self.pixmap_label.setMinimumSize(QSize(16, 16))
        self.pixmap_label.setMaximumSize(QSize(16, 16))

        self.horizontalLayout.addWidget(self.pixmap_label)

        self.message_label = QLabel(MoreInfoWidget)
        self.message_label.setObjectName(u"message_label")

        self.horizontalLayout.addWidget(self.message_label)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 10)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.text_edit = QTextEdit(MoreInfoWidget)
        self.text_edit.setObjectName(u"text_edit")
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)
        self.text_edit.setReadOnly(True)

        self.verticalLayout.addWidget(self.text_edit)

        self.retranslateUi(MoreInfoWidget)

        QMetaObject.connectSlotsByName(MoreInfoWidget)
    # setupUi

    def retranslateUi(self, MoreInfoWidget):
        MoreInfoWidget.setWindowTitle(QCoreApplication.translate("MoreInfoWidget", u"Form", None))
        self.pixmap_label.setText("")
        self.message_label.setText(QCoreApplication.translate("MoreInfoWidget", u"More Info...", None))
    # retranslateUi
