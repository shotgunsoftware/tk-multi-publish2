# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'context_widget.ui'
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


from  . import resources_rc

class Ui_ContextWidget(object):
    def setupUi(self, ContextWidget):
        if not ContextWidget.objectName():
            ContextWidget.setObjectName(u"ContextWidget")
        ContextWidget.resize(252, 16)
        self.verticalLayout = QVBoxLayout(ContextWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(ContextWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.header = QLabel(self.frame)
        self.header.setObjectName(u"header")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.header)

        self.checkbox = QCheckBox(self.frame)
        self.checkbox.setObjectName(u"checkbox")

        self.horizontalLayout.addWidget(self.checkbox)

        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(ContextWidget)

        QMetaObject.connectSlotsByName(ContextWidget)
    # setupUi

    def retranslateUi(self, ContextWidget):
        ContextWidget.setWindowTitle(QCoreApplication.translate("ContextWidget", u"Form", None))
        self.header.setText(QCoreApplication.translate("ContextWidget", u"context", None))
#if QT_CONFIG(tooltip)
        self.checkbox.setToolTip(QCoreApplication.translate("ContextWidget", u"hint: shift-click to toggle all items of this type", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi
