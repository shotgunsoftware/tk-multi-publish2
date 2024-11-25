# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'progress_details_widget.ui'
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

class Ui_ProgressDetailsWidget(object):
    def setupUi(self, ProgressDetailsWidget):
        if not ProgressDetailsWidget.objectName():
            ProgressDetailsWidget.setObjectName(u"ProgressDetailsWidget")
        ProgressDetailsWidget.resize(370, 233)
        self.verticalLayout = QVBoxLayout(ProgressDetailsWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.progress_frame = QFrame(ProgressDetailsWidget)
        self.progress_frame.setObjectName(u"progress_frame")
        self.progress_frame.setFrameShape(QFrame.StyledPanel)
        self.progress_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.progress_frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.progress_label = QLabel(self.progress_frame)
        self.progress_label.setObjectName(u"progress_label")

        self.horizontalLayout.addWidget(self.progress_label)

        self.copy_log_button = QToolButton(self.progress_frame)
        self.copy_log_button.setObjectName(u"copy_log_button")
        self.copy_log_button.setMinimumSize(QSize(105, 0))
        self.copy_log_button.setToolButtonStyle(Qt.ToolButtonTextOnly)

        self.horizontalLayout.addWidget(self.copy_log_button)

        self.close = QToolButton(self.progress_frame)
        self.close.setObjectName(u"close")
        self.close.setMinimumSize(QSize(30, 30))
        self.close.setMaximumSize(QSize(30, 30))
        icon = QIcon()
        icon.addFile(u":/tk_multi_publish2/cross.png", QSize(), QIcon.Normal, QIcon.Off)
        self.close.setIcon(icon)
        self.close.setIconSize(QSize(30, 30))

        self.horizontalLayout.addWidget(self.close)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.log_tree = QTreeWidget(self.progress_frame)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(1, u"2");
        __qtreewidgetitem.setText(0, u"1");
        self.log_tree.setHeaderItem(__qtreewidgetitem)
        self.log_tree.setObjectName(u"log_tree")
        self.log_tree.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
        self.log_tree.setUniformRowHeights(True)
        self.log_tree.setWordWrap(True)
        self.log_tree.setColumnCount(2)
        self.log_tree.header().setVisible(False)
        self.log_tree.header().setStretchLastSection(False)

        self.verticalLayout_2.addWidget(self.log_tree)

        self.verticalLayout.addWidget(self.progress_frame)

        self.retranslateUi(ProgressDetailsWidget)

        QMetaObject.connectSlotsByName(ProgressDetailsWidget)
    # setupUi

    def retranslateUi(self, ProgressDetailsWidget):
        ProgressDetailsWidget.setWindowTitle(QCoreApplication.translate("ProgressDetailsWidget", u"Form", None))
        self.progress_label.setText(QCoreApplication.translate("ProgressDetailsWidget", u"Progress Details", None))
#if QT_CONFIG(tooltip)
        self.copy_log_button.setToolTip(QCoreApplication.translate("ProgressDetailsWidget", u"<html><head/><body><p>Open the publisher's log file. The log file is useful for deeper debugging of publish issues. For issues involving Flow Production Tracking Support, please include a copy of this file when submitting a support request. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.copy_log_button.setText(QCoreApplication.translate("ProgressDetailsWidget", u"Copy to Clipboard", None))
#if QT_CONFIG(tooltip)
        self.close.setToolTip(QCoreApplication.translate("ProgressDetailsWidget", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.close.setText("")
#if QT_CONFIG(accessibility)
        self.log_tree.setAccessibleName(QCoreApplication.translate("ProgressDetailsWidget", u"<html><head/><body><p>Opens the log file for the current engine which will include log messages from the publisher. This file is extremely useful for deeper debugging and understanding of publish issues. A copy of this file should be included when submitting support requests to the Flow Production Tracking Support team.</p></body></html>", None))
#endif // QT_CONFIG(accessibility)
    # retranslateUi
