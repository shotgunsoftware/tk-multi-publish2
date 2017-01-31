# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(884, 639)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.verticalLayoutWidget = QtGui.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.frame = DropAreaFrame(self.verticalLayoutWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.stackedWidget = QtGui.QStackedWidget(self.frame)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtGui.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_15 = QtGui.QVBoxLayout(self.page)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.items_tree = QtGui.QTreeWidget(self.page)
        self.items_tree.setObjectName("items_tree")
        self.items_tree.headerItem().setText(0, "1")
        self.items_tree.header().setVisible(False)
        self.verticalLayout_15.addWidget(self.items_tree)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.page_2)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.items_tree_2 = QtGui.QTreeWidget(self.page_2)
        self.items_tree_2.setObjectName("items_tree_2")
        self.items_tree_2.headerItem().setText(0, "1")
        self.items_tree_2.header().setVisible(False)
        self.verticalLayout_14.addWidget(self.items_tree_2)
        self.stackedWidget.addWidget(self.page_2)
        self.verticalLayout_2.addWidget(self.stackedWidget)
        self.verticalLayout.addWidget(self.frame)
        self.right_tabs = QtGui.QTabWidget(self.splitter)
        self.right_tabs.setObjectName("right_tabs")
        self.details_tab = QtGui.QWidget()
        self.details_tab.setObjectName("details_tab")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.details_tab)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.details_stack = QtGui.QStackedWidget(self.details_tab)
        self.details_stack.setObjectName("details_stack")
        self.details_summary = QtGui.QWidget()
        self.details_summary.setObjectName("details_summary")
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.details_summary)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.summary_icon = QtGui.QLabel(self.details_summary)
        self.summary_icon.setMinimumSize(QtCore.QSize(60, 60))
        self.summary_icon.setMaximumSize(QtCore.QSize(60, 60))
        self.summary_icon.setText("")
        self.summary_icon.setScaledContents(True)
        self.summary_icon.setObjectName("summary_icon")
        self.horizontalLayout_2.addWidget(self.summary_icon)
        self.summary_header = QtGui.QLabel(self.details_summary)
        self.summary_header.setWordWrap(True)
        self.summary_header.setObjectName("summary_header")
        self.horizontalLayout_2.addWidget(self.summary_header)
        self.verticalLayout_9.addLayout(self.horizontalLayout_2)
        self.summary_divider = QtGui.QFrame(self.details_summary)
        self.summary_divider.setFrameShape(QtGui.QFrame.HLine)
        self.summary_divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.summary_divider.setObjectName("summary_divider")
        self.verticalLayout_9.addWidget(self.summary_divider)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_2 = QtGui.QLabel(self.details_summary)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_7.addWidget(self.label_2)
        self.summary_thumbnail = Thumbnail(self.details_summary)
        self.summary_thumbnail.setMinimumSize(QtCore.QSize(160, 90))
        self.summary_thumbnail.setMaximumSize(QtCore.QSize(160, 90))
        self.summary_thumbnail.setText("")
        self.summary_thumbnail.setScaledContents(True)
        self.summary_thumbnail.setObjectName("summary_thumbnail")
        self.verticalLayout_7.addWidget(self.summary_thumbnail)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem)
        self.horizontalLayout_3.addLayout(self.verticalLayout_7)
        self.verticalLayout_8 = QtGui.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_3 = QtGui.QLabel(self.details_summary)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_8.addWidget(self.label_3)
        self.summary_comments = QtGui.QPlainTextEdit(self.details_summary)
        self.summary_comments.setObjectName("summary_comments")
        self.verticalLayout_8.addWidget(self.summary_comments)
        self.horizontalLayout_3.addLayout(self.verticalLayout_8)
        self.verticalLayout_9.addLayout(self.horizontalLayout_3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_9.addItem(spacerItem1)
        self.details_stack.addWidget(self.details_summary)
        self.details_task = QtGui.QWidget()
        self.details_task.setObjectName("details_task")
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.details_task)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.task_icon = QtGui.QLabel(self.details_task)
        self.task_icon.setMinimumSize(QtCore.QSize(60, 60))
        self.task_icon.setMaximumSize(QtCore.QSize(60, 60))
        self.task_icon.setText("")
        self.task_icon.setScaledContents(True)
        self.task_icon.setObjectName("task_icon")
        self.horizontalLayout_4.addWidget(self.task_icon)
        self.task_name = QtGui.QLabel(self.details_task)
        self.task_name.setObjectName("task_name")
        self.horizontalLayout_4.addWidget(self.task_name)
        self.verticalLayout_11.addLayout(self.horizontalLayout_4)
        self.task_description = QtGui.QLabel(self.details_task)
        self.task_description.setWordWrap(True)
        self.task_description.setObjectName("task_description")
        self.verticalLayout_11.addWidget(self.task_description)
        self.task_settings_label = QtGui.QLabel(self.details_task)
        self.task_settings_label.setObjectName("task_settings_label")
        self.verticalLayout_11.addWidget(self.task_settings_label)
        self.task_divider = QtGui.QFrame(self.details_task)
        self.task_divider.setFrameShape(QtGui.QFrame.HLine)
        self.task_divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.task_divider.setObjectName("task_divider")
        self.verticalLayout_11.addWidget(self.task_divider)
        self.task_settings = SettingsWidget(self.details_task)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_settings.sizePolicy().hasHeightForWidth())
        self.task_settings.setSizePolicy(sizePolicy)
        self.task_settings.setObjectName("task_settings")
        self.verticalLayout_11.addWidget(self.task_settings)
        self.details_stack.addWidget(self.details_task)
        self.details_plugin = QtGui.QWidget()
        self.details_plugin.setObjectName("details_plugin")
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.details_plugin)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.plugin_icon = QtGui.QLabel(self.details_plugin)
        self.plugin_icon.setMinimumSize(QtCore.QSize(60, 60))
        self.plugin_icon.setMaximumSize(QtCore.QSize(60, 60))
        self.plugin_icon.setText("")
        self.plugin_icon.setScaledContents(True)
        self.plugin_icon.setObjectName("plugin_icon")
        self.horizontalLayout_5.addWidget(self.plugin_icon)
        self.plugin_name = QtGui.QLabel(self.details_plugin)
        self.plugin_name.setObjectName("plugin_name")
        self.horizontalLayout_5.addWidget(self.plugin_name)
        self.verticalLayout_10.addLayout(self.horizontalLayout_5)
        self.plugin_description = QtGui.QLabel(self.details_plugin)
        self.plugin_description.setWordWrap(True)
        self.plugin_description.setObjectName("plugin_description")
        self.verticalLayout_10.addWidget(self.plugin_description)
        self.plugin_settings_label = QtGui.QLabel(self.details_plugin)
        self.plugin_settings_label.setObjectName("plugin_settings_label")
        self.verticalLayout_10.addWidget(self.plugin_settings_label)
        self.plugin_divider = QtGui.QFrame(self.details_plugin)
        self.plugin_divider.setFrameShape(QtGui.QFrame.HLine)
        self.plugin_divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.plugin_divider.setObjectName("plugin_divider")
        self.verticalLayout_10.addWidget(self.plugin_divider)
        self.plugin_settings = SettingsWidget(self.details_plugin)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plugin_settings.sizePolicy().hasHeightForWidth())
        self.plugin_settings.setSizePolicy(sizePolicy)
        self.plugin_settings.setObjectName("plugin_settings")
        self.verticalLayout_10.addWidget(self.plugin_settings)
        self.details_stack.addWidget(self.details_plugin)
        self.details_item = QtGui.QWidget()
        self.details_item.setObjectName("details_item")
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.details_item)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.item_icon = QtGui.QLabel(self.details_item)
        self.item_icon.setMinimumSize(QtCore.QSize(60, 60))
        self.item_icon.setMaximumSize(QtCore.QSize(60, 60))
        self.item_icon.setText("")
        self.item_icon.setScaledContents(True)
        self.item_icon.setObjectName("item_icon")
        self.horizontalLayout_6.addWidget(self.item_icon)
        self.verticalLayout_12 = QtGui.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.item_name = QtGui.QLabel(self.details_item)
        self.item_name.setObjectName("item_name")
        self.verticalLayout_12.addWidget(self.item_name)
        self.item_type = QtGui.QLabel(self.details_item)
        self.item_type.setObjectName("item_type")
        self.verticalLayout_12.addWidget(self.item_type)
        self.horizontalLayout_6.addLayout(self.verticalLayout_12)
        self.verticalLayout_13.addLayout(self.horizontalLayout_6)
        self.item_settings_label = QtGui.QLabel(self.details_item)
        self.item_settings_label.setObjectName("item_settings_label")
        self.verticalLayout_13.addWidget(self.item_settings_label)
        self.item_divider = QtGui.QFrame(self.details_item)
        self.item_divider.setFrameShape(QtGui.QFrame.HLine)
        self.item_divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.item_divider.setObjectName("item_divider")
        self.verticalLayout_13.addWidget(self.item_divider)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.item_thumbnail = Thumbnail(self.details_item)
        self.item_thumbnail.setMinimumSize(QtCore.QSize(160, 90))
        self.item_thumbnail.setMaximumSize(QtCore.QSize(160, 90))
        self.item_thumbnail.setText("")
        self.item_thumbnail.setScaledContents(True)
        self.item_thumbnail.setObjectName("item_thumbnail")
        self.horizontalLayout_7.addWidget(self.item_thumbnail)
        self.item_description_2 = QtGui.QLabel(self.details_item)
        self.item_description_2.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.item_description_2.setWordWrap(True)
        self.item_description_2.setObjectName("item_description_2")
        self.horizontalLayout_7.addWidget(self.item_description_2)
        self.verticalLayout_13.addLayout(self.horizontalLayout_7)
        self.item_settings = SettingsWidget(self.details_item)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item_settings.sizePolicy().hasHeightForWidth())
        self.item_settings.setSizePolicy(sizePolicy)
        self.item_settings.setObjectName("item_settings")
        self.verticalLayout_13.addWidget(self.item_settings)
        self.details_stack.addWidget(self.details_item)
        self.details_select = QtGui.QWidget()
        self.details_select.setObjectName("details_select")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.details_select)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.please_select_an_item = QtGui.QLabel(self.details_select)
        self.please_select_an_item.setAlignment(QtCore.Qt.AlignCenter)
        self.please_select_an_item.setObjectName("please_select_an_item")
        self.verticalLayout_6.addWidget(self.please_select_an_item)
        self.details_stack.addWidget(self.details_select)
        self.verticalLayout_5.addWidget(self.details_stack)
        self.right_tabs.addTab(self.details_tab, "")
        self.progress_tab = QtGui.QWidget()
        self.progress_tab.setObjectName("progress_tab")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.progress_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.log_tree = QtGui.QTreeWidget(self.progress_tab)
        self.log_tree.setObjectName("log_tree")
        self.log_tree.headerItem().setText(0, "1")
        self.log_tree.header().setVisible(False)
        self.verticalLayout_4.addWidget(self.log_tree)
        self.right_tabs.addTab(self.progress_tab, "")
        self.verticalLayout_3.addWidget(self.splitter)
        self.bottom_frame = QtGui.QFrame(Dialog)
        self.bottom_frame.setMaximumSize(QtCore.QSize(16777215, 40))
        self.bottom_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.bottom_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.bottom_frame.setObjectName("bottom_frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.bottom_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.options = QtGui.QPushButton(self.bottom_frame)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/tick.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.options.setIcon(icon)
        self.options.setObjectName("options")
        self.horizontalLayout.addWidget(self.options)
        self.swap = QtGui.QPushButton(self.bottom_frame)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/yinyang.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.swap.setIcon(icon1)
        self.swap.setObjectName("swap")
        self.horizontalLayout.addWidget(self.swap)
        self.validate = QtGui.QPushButton(self.bottom_frame)
        self.validate.setObjectName("validate")
        self.horizontalLayout.addWidget(self.validate)
        spacerItem2 = QtGui.QSpacerItem(638, 11, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.publish = QtGui.QPushButton(self.bottom_frame)
        self.publish.setObjectName("publish")
        self.horizontalLayout.addWidget(self.publish)
        self.verticalLayout_3.addWidget(self.bottom_frame)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(0)
        self.right_tabs.setCurrentIndex(0)
        self.details_stack.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Shotgun Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Please choose items to publish", None, QtGui.QApplication.UnicodeUTF8))
        self.summary_header.setText(QtGui.QApplication.translate("Dialog", "SUMMARY", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Thumbnail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.task_name.setText(QtGui.QApplication.translate("Dialog", "Task Name", None, QtGui.QApplication.UnicodeUTF8))
        self.task_description.setText(QtGui.QApplication.translate("Dialog", "task desc", None, QtGui.QApplication.UnicodeUTF8))
        self.task_settings_label.setText(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.plugin_name.setText(QtGui.QApplication.translate("Dialog", "Plugin Name", None, QtGui.QApplication.UnicodeUTF8))
        self.plugin_description.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.plugin_settings_label.setText(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.item_name.setText(QtGui.QApplication.translate("Dialog", "Item name", None, QtGui.QApplication.UnicodeUTF8))
        self.item_type.setText(QtGui.QApplication.translate("Dialog", "Item type", None, QtGui.QApplication.UnicodeUTF8))
        self.item_settings_label.setText(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.item_description_2.setText(QtGui.QApplication.translate("Dialog", "The thumbnail will be associated\n"
"with all related publishes.\n"
"Click to take a screen grab.", None, QtGui.QApplication.UnicodeUTF8))
        self.please_select_an_item.setText(QtGui.QApplication.translate("Dialog", "Please select an item \n"
"for more details", None, QtGui.QApplication.UnicodeUTF8))
        self.right_tabs.setTabText(self.right_tabs.indexOf(self.details_tab), QtGui.QApplication.translate("Dialog", "Details", None, QtGui.QApplication.UnicodeUTF8))
        self.right_tabs.setTabText(self.right_tabs.indexOf(self.progress_tab), QtGui.QApplication.translate("Dialog", "Progress", None, QtGui.QApplication.UnicodeUTF8))
        self.validate.setText(QtGui.QApplication.translate("Dialog", "Validate", None, QtGui.QApplication.UnicodeUTF8))
        self.publish.setText(QtGui.QApplication.translate("Dialog", "Publish", None, QtGui.QApplication.UnicodeUTF8))

from ..settings_widget import SettingsWidget
from ..drop_area import DropAreaFrame
from ..thumbnail import Thumbnail
from . import resources_rc
