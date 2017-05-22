# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'context_editor_widget.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_ContextWidget(object):
    def setupUi(self, ContextWidget):
        ContextWidget.setObjectName("ContextWidget")
        ContextWidget.resize(294, 60)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ContextWidget.sizePolicy().hasHeightForWidth())
        ContextWidget.setSizePolicy(sizePolicy)
        ContextWidget.setMinimumSize(QtCore.QSize(0, 60))
        self.verticalLayout = QtGui.QVBoxLayout(ContextWidget)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.context_help_lbl = QtGui.QLabel(ContextWidget)
        self.context_help_lbl.setObjectName("context_help_lbl")
        self.verticalLayout.addWidget(self.context_help_lbl)
        self.context_layout = QtGui.QHBoxLayout()
        self.context_layout.setSpacing(0)
        self.context_layout.setObjectName("context_layout")
        self.context_label = QtGui.QLabel(ContextWidget)
        self.context_label.setMinimumSize(QtCore.QSize(0, 32))
        self.context_label.setMargin(4)
        self.context_label.setOpenExternalLinks(True)
        self.context_label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.context_label.setObjectName("context_label")
        self.context_layout.addWidget(self.context_label)
        self.context_search = GlobalSearchWidget(ContextWidget)
        self.context_search.setMinimumSize(QtCore.QSize(24, 32))
        self.context_search.setObjectName("context_search")
        self.context_layout.addWidget(self.context_search)
        self.context_search_btn = QtGui.QToolButton(ContextWidget)
        self.context_search_btn.setMinimumSize(QtCore.QSize(32, 32))
        self.context_search_btn.setMaximumSize(QtCore.QSize(32, 32))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.context_search_btn.setIcon(icon)
        self.context_search_btn.setIconSize(QtCore.QSize(32, 32))
        self.context_search_btn.setCheckable(True)
        self.context_search_btn.setObjectName("context_search_btn")
        self.context_layout.addWidget(self.context_search_btn)
        self.context_menu_btn = QtGui.QToolButton(ContextWidget)
        self.context_menu_btn.setMinimumSize(QtCore.QSize(32, 32))
        self.context_menu_btn.setMaximumSize(QtCore.QSize(32, 32))
        self.context_menu_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/down_arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.context_menu_btn.setIcon(icon1)
        self.context_menu_btn.setIconSize(QtCore.QSize(32, 32))
        self.context_menu_btn.setCheckable(False)
        self.context_menu_btn.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.context_menu_btn.setObjectName("context_menu_btn")
        self.context_layout.addWidget(self.context_menu_btn)
        self.context_layout.setStretch(0, 4)
        self.context_layout.setStretch(1, 4)
        self.context_layout.setStretch(2, 1)
        self.context_layout.setStretch(3, 1)
        self.verticalLayout.addLayout(self.context_layout)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ContextWidget)
        QtCore.QMetaObject.connectSlotsByName(ContextWidget)

    def retranslateUi(self, ContextWidget):
        ContextWidget.setWindowTitle(QtGui.QApplication.translate("ContextWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.context_help_lbl.setText(QtGui.QApplication.translate("ContextWidget", "Link this item to a Shotgun entity or task:", None, QtGui.QApplication.UnicodeUTF8))
        self.context_label.setToolTip(QtGui.QApplication.translate("ContextWidget", "<html><head/><body><p>The context for the currently selected item on the left. Click the name to go to that context in Shotgun.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.context_label.setText(QtGui.QApplication.translate("ContextWidget", "Loading...", None, QtGui.QApplication.UnicodeUTF8))
        self.context_search.setToolTip(QtGui.QApplication.translate("ContextWidget", "<html><head/><body><p>Type in this box to find a Shotgun entity or task to associate with the currently selected item to publish.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.context_search_btn.setToolTip(QtGui.QApplication.translate("ContextWidget", "<html><head/><body><p>Toggle this button to allow searching for a context to link to the selected publish item.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.context_search_btn.setText(QtGui.QApplication.translate("ContextWidget", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.context_menu_btn.setToolTip(QtGui.QApplication.translate("ContextWidget", "<html><head/><body><p>Show a menu for recently used contexts and tasks assigned to you. </p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

from ..qtwidgets import GlobalSearchWidget
from . import resources_rc
