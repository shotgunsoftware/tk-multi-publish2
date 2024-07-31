# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'item_widget.ui'
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

class Ui_ItemWidget(object):
    def setupUi(self, ItemWidget):
        if not ItemWidget.objectName():
            ItemWidget.setObjectName(u"ItemWidget")
        ItemWidget.resize(313, 46)
        ItemWidget.setMinimumSize(QSize(0, 45))
        self.verticalLayout = QVBoxLayout(ItemWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(ItemWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(4, 2, 2, 2)
        self.expand_placeholder = QWidget(self.frame)
        self.expand_placeholder.setObjectName(u"expand_placeholder")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.expand_placeholder.sizePolicy().hasHeightForWidth())
        self.expand_placeholder.setSizePolicy(sizePolicy)
        self.expand_placeholder.setMinimumSize(QSize(16, 16))
        self.expand_placeholder.setMaximumSize(QSize(16, 16))

        self.horizontalLayout.addWidget(self.expand_placeholder)

        self.expand_indicator = QToolButton(self.frame)
        self.expand_indicator.setObjectName(u"expand_indicator")
        self.expand_indicator.setMinimumSize(QSize(16, 16))
        self.expand_indicator.setMaximumSize(QSize(16, 16))
        icon1 = QIcon()
        icon1.addFile(u":/tk_multi_publish2/down_arrow.png", QSize(), QIcon.Normal, QIcon.Off)
        self.expand_indicator.setIcon(icon1)

        self.horizontalLayout.addWidget(self.expand_indicator)

        self.icon = QLabel(self.frame)
        self.icon.setObjectName(u"icon")
        self.icon.setMinimumSize(QSize(32, 32))
        self.icon.setMaximumSize(QSize(30, 30))
        self.icon.setScaledContents(True)

        self.horizontalLayout.addWidget(self.icon)

        self.header = QLabel(self.frame)
        self.header.setObjectName(u"header")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy1)
        self.header.setMinimumSize(QSize(1, 1))
        self.header.setTextInteractionFlags(Qt.NoTextInteraction)

        self.horizontalLayout.addWidget(self.header)

        self.handle_stack = QStackedWidget(self.frame)
        self.handle_stack.setObjectName(u"handle_stack")
        self.handle_stack.setMinimumSize(QSize(22, 22))
        self.handle_stack.setMaximumSize(QSize(22, 22))
        self.drag = QWidget()
        self.drag.setObjectName(u"drag")
        self.horizontalLayout_2 = QHBoxLayout(self.drag)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.drag_handle = QLabel(self.drag)
        self.drag_handle.setObjectName(u"drag_handle")
        self.drag_handle.setMinimumSize(QSize(16, 16))
        self.drag_handle.setMaximumSize(QSize(16, 16))
        self.drag_handle.setCursor(QCursor(Qt.OpenHandCursor))
        self.drag_handle.setPixmap(QPixmap(u":/tk_multi_publish2/drag_handle.png"))
        self.drag_handle.setScaledContents(True)

        self.horizontalLayout_2.addWidget(self.drag_handle)

        self.handle_stack.addWidget(self.drag)
        self.lock = QWidget()
        self.lock.setObjectName(u"lock")
        self.horizontalLayout_3 = QHBoxLayout(self.lock)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.locked_handle = QLabel(self.lock)
        self.locked_handle.setObjectName(u"locked_handle")
        self.locked_handle.setMinimumSize(QSize(16, 16))
        self.locked_handle.setMaximumSize(QSize(16, 16))
        self.locked_handle.setScaledContents(True)

        self.horizontalLayout_3.addWidget(self.locked_handle)

        self.handle_stack.addWidget(self.lock)

        self.horizontalLayout.addWidget(self.handle_stack)

        self.status = QToolButton(self.frame)
        self.status.setObjectName(u"status")
        self.status.setMinimumSize(QSize(30, 30))
        self.status.setMaximumSize(QSize(30, 30))
        icon2 = QIcon()
        icon2.addFile(u":/tk_multi_publish2/status_validate.png", QSize(), QIcon.Normal, QIcon.Off)
        self.status.setIcon(icon2)
        self.status.setIconSize(QSize(24, 24))

        self.horizontalLayout.addWidget(self.status)

        self.checkbox = QCheckBox(self.frame)
        self.checkbox.setObjectName(u"checkbox")

        self.horizontalLayout.addWidget(self.checkbox)

        self.horizontalLayout.setStretch(3, 10)

        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(ItemWidget)

        self.handle_stack.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(ItemWidget)
    # setupUi

    def retranslateUi(self, ItemWidget):
        ItemWidget.setWindowTitle(QCoreApplication.translate("ItemWidget", u"Form", None))
#if QT_CONFIG(accessibility)
        ItemWidget.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item widget", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.frame.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item inner frame", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.expand_placeholder.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item expand", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.expand_indicator.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item expand indicator", None))
#endif // QT_CONFIG(accessibility)
        self.expand_indicator.setText("")
        self.icon.setText("")
        self.header.setText(QCoreApplication.translate("ItemWidget", u"<big>Alembic Caches</big><br>foo", None))
#if QT_CONFIG(accessibility)
        self.handle_stack.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item stackedwidget", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(tooltip)
        self.drag_handle.setToolTip(QCoreApplication.translate("ItemWidget", u"Drag & drop enabled for changing this item's context", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.drag_handle.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item drag handle", None))
#endif // QT_CONFIG(accessibility)
        self.drag_handle.setText("")
#if QT_CONFIG(tooltip)
        self.locked_handle.setToolTip(QCoreApplication.translate("ItemWidget", u"Context change is not allowed for this item", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.locked_handle.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item lock handle", None))
#endif // QT_CONFIG(accessibility)
        self.locked_handle.setText("")
#if QT_CONFIG(tooltip)
        self.status.setToolTip(QCoreApplication.translate("ItemWidget", u"Click for details", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.status.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item status", None))
#endif // QT_CONFIG(accessibility)
        self.status.setText(QCoreApplication.translate("ItemWidget", u"...", None))
#if QT_CONFIG(accessibility)
        self.checkbox.setAccessibleName(QCoreApplication.translate("ItemWidget", u"item checkbox", None))
#endif // QT_CONFIG(accessibility)
        self.checkbox.setText("")
    # retranslateUi
