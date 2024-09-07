# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'task_widget.ui'
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

class Ui_TaskWidget(object):
    def setupUi(self, TaskWidget):
        if not TaskWidget.objectName():
            TaskWidget.setObjectName(u"TaskWidget")
        TaskWidget.resize(338, 36)
        self.verticalLayout = QVBoxLayout(TaskWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(TaskWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 32))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 2, 2, 2)
        self.icon = QLabel(self.frame)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(18, 18))
        self.icon.setMaximumSize(QSize(18, 18))
        self.icon.setPixmap(QPixmap(u":/tk_multi_publish2/shotgun.png"))
        self.icon.setScaledContents(True)
        self.icon.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.icon)

        self.header = QLabel(self.frame)
        self.header.setObjectName(u"header")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setMinimumSize(QSize(1, 1))

        self.horizontalLayout.addWidget(self.header)

        self.status = QToolButton(self.frame)
        self.status.setObjectName(u"status")
        self.status.setMinimumSize(QSize(30, 22))
        self.status.setMaximumSize(QSize(30, 22))
        icon1 = QIcon()
        icon1.addFile(u":/tk_multi_publish2/status_publish.png", QSize(), QIcon.Normal, QIcon.Off)
        self.status.setIcon(icon1)
        self.status.setIconSize(QSize(16, 16))

        self.horizontalLayout.addWidget(self.status)

        self.checkbox = QCheckBox(self.frame)
        self.checkbox.setObjectName(u"checkbox")

        self.horizontalLayout.addWidget(self.checkbox)

        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(TaskWidget)

        QMetaObject.connectSlotsByName(TaskWidget)
    # setupUi

    def retranslateUi(self, TaskWidget):
        TaskWidget.setWindowTitle(QCoreApplication.translate("TaskWidget", u"Form", None))
#if QT_CONFIG(accessibility)
        TaskWidget.setAccessibleName(QCoreApplication.translate("TaskWidget", u"task widget", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.frame.setAccessibleName(QCoreApplication.translate("TaskWidget", u"task widget inner frame", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.icon.setAccessibleName(QCoreApplication.translate("TaskWidget", u"task icon", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.header.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.header.setText(QCoreApplication.translate("TaskWidget", u"<big>Alembic Caches</big>", None))
#if QT_CONFIG(tooltip)
        self.status.setToolTip(QCoreApplication.translate("TaskWidget", u"Click for more details", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.status.setAccessibleName(QCoreApplication.translate("TaskWidget", u"task status", None))
#endif // QT_CONFIG(accessibility)
        self.status.setText(QCoreApplication.translate("TaskWidget", u"...", None))
#if QT_CONFIG(tooltip)
        self.checkbox.setToolTip(QCoreApplication.translate("TaskWidget", u"hint: shift-click to toggle all items of this type", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.checkbox.setAccessibleName(QCoreApplication.translate("TaskWidget", u"task checkbox", None))
#endif // QT_CONFIG(accessibility)
    # retranslateUi
