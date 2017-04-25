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
        Dialog.resize(798, 593)
        self.verticalLayout_7 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.main_stack = QtGui.QStackedWidget(Dialog)
        self.main_stack.setObjectName("main_stack")
        self.large_drop_area_frame = QtGui.QWidget()
        self.large_drop_area_frame.setObjectName("large_drop_area_frame")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.large_drop_area_frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.large_drop_area = DropAreaFrame(self.large_drop_area_frame)
        self.large_drop_area.setFrameShape(QtGui.QFrame.StyledPanel)
        self.large_drop_area.setFrameShadow(QtGui.QFrame.Raised)
        self.large_drop_area.setObjectName("large_drop_area")
        self.verticalLayout = QtGui.QVBoxLayout(self.large_drop_area)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 98, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.label_5 = QtGui.QLabel(self.large_drop_area)
        self.label_5.setMinimumSize(QtCore.QSize(128, 128))
        self.label_5.setMaximumSize(QtCore.QSize(128, 128))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/icon_256.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.large_drop_area_label = QtGui.QLabel(self.large_drop_area)
        self.large_drop_area_label.setAlignment(QtCore.Qt.AlignCenter)
        self.large_drop_area_label.setObjectName("large_drop_area_label")
        self.verticalLayout.addWidget(self.large_drop_area_label)
        spacerItem3 = QtGui.QSpacerItem(20, 213, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.verticalLayout_3.addWidget(self.large_drop_area)
        self.main_stack.addWidget(self.large_drop_area_frame)
        self.main_ui_frame = QtGui.QWidget()
        self.main_ui_frame.setObjectName("main_ui_frame")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.main_ui_frame)
        self.verticalLayout_4.setSpacing(2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.main_frame = QtGui.QWidget(self.main_ui_frame)
        self.main_frame.setObjectName("main_frame")
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.main_frame)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.splitter = QtGui.QSplitter(self.main_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.frame = DropAreaFrame(self.splitter)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.items_tree = PublishTreeWidget(self.frame)
        self.items_tree.setAcceptDrops(True)
        self.items_tree.setDragEnabled(True)
        self.items_tree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.items_tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.items_tree.setObjectName("items_tree")
        self.items_tree.headerItem().setText(0, "1")
        self.items_tree.header().setVisible(False)
        self.verticalLayout_2.addWidget(self.items_tree)
        self.text_below_item_tree = QtGui.QLabel(self.frame)
        self.text_below_item_tree.setAlignment(QtCore.Qt.AlignCenter)
        self.text_below_item_tree.setObjectName("text_below_item_tree")
        self.verticalLayout_2.addWidget(self.text_below_item_tree)
        self.details_frame = QtGui.QFrame(self.splitter)
        self.details_frame.setObjectName("details_frame")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.details_frame)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.details_stack = QtGui.QStackedWidget(self.details_frame)
        self.details_stack.setObjectName("details_stack")
        self.details_item = QtGui.QWidget()
        self.details_item.setObjectName("details_item")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.details_item)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.item_icon = QtGui.QLabel(self.details_item)
        self.item_icon.setMinimumSize(QtCore.QSize(60, 60))
        self.item_icon.setMaximumSize(QtCore.QSize(60, 60))
        self.item_icon.setText("")
        self.item_icon.setScaledContents(True)
        self.item_icon.setObjectName("item_icon")
        self.horizontalLayout_2.addWidget(self.item_icon)
        self.verticalLayout_12 = QtGui.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.item_name = QtGui.QLabel(self.details_item)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item_name.sizePolicy().hasHeightForWidth())
        self.item_name.setSizePolicy(sizePolicy)
        self.item_name.setObjectName("item_name")
        self.verticalLayout_12.addWidget(self.item_name)
        self.item_type = QtGui.QLabel(self.details_item)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item_type.sizePolicy().hasHeightForWidth())
        self.item_type.setSizePolicy(sizePolicy)
        self.item_type.setObjectName("item_type")
        self.verticalLayout_12.addWidget(self.item_type)
        self.horizontalLayout_2.addLayout(self.verticalLayout_12)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.item_divider_1 = QtGui.QFrame(self.details_item)
        self.item_divider_1.setFrameShape(QtGui.QFrame.HLine)
        self.item_divider_1.setFrameShadow(QtGui.QFrame.Sunken)
        self.item_divider_1.setObjectName("item_divider_1")
        self.verticalLayout_6.addWidget(self.item_divider_1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(30)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.link_label = QtGui.QLabel(self.details_item)
        self.link_label.setObjectName("link_label")
        self.horizontalLayout_5.addWidget(self.link_label)
        self.context_widget = ContextWidget(self.details_item)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.context_widget.sizePolicy().hasHeightForWidth())
        self.context_widget.setSizePolicy(sizePolicy)
        self.context_widget.setObjectName("context_widget")
        self.horizontalLayout_5.addWidget(self.context_widget)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtGui.QLabel(self.details_item)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.item_comments = QtGui.QPlainTextEdit(self.details_item)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item_comments.sizePolicy().hasHeightForWidth())
        self.item_comments.setSizePolicy(sizePolicy)
        self.item_comments.setMinimumSize(QtCore.QSize(0, 90))
        self.item_comments.setMaximumSize(QtCore.QSize(16777215, 90))
        self.item_comments.setObjectName("item_comments")
        self.gridLayout.addWidget(self.item_comments, 2, 1, 1, 2)
        self.label_6 = QtGui.QLabel(self.details_item)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 1, 1, 2)
        self.item_thumbnail = Thumbnail(self.details_item)
        self.item_thumbnail.setMinimumSize(QtCore.QSize(160, 90))
        self.item_thumbnail.setMaximumSize(QtCore.QSize(160, 90))
        self.item_thumbnail.setText("")
        self.item_thumbnail.setScaledContents(True)
        self.item_thumbnail.setObjectName("item_thumbnail")
        self.gridLayout.addWidget(self.item_thumbnail, 2, 0, 1, 1)
        self.verticalLayout_6.addLayout(self.gridLayout)
        self.item_summary_label = QtGui.QLabel(self.details_item)
        self.item_summary_label.setObjectName("item_summary_label")
        self.verticalLayout_6.addWidget(self.item_summary_label)
        self.item_summary = QtGui.QLabel(self.details_item)
        self.item_summary.setText("")
        self.item_summary.setWordWrap(True)
        self.item_summary.setObjectName("item_summary")
        self.verticalLayout_6.addWidget(self.item_summary)
        self.item_settings_label = QtGui.QLabel(self.details_item)
        self.item_settings_label.setObjectName("item_settings_label")
        self.verticalLayout_6.addWidget(self.item_settings_label)
        self.item_settings = SettingsWidget(self.details_item)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item_settings.sizePolicy().hasHeightForWidth())
        self.item_settings.setSizePolicy(sizePolicy)
        self.item_settings.setObjectName("item_settings")
        self.verticalLayout_6.addWidget(self.item_settings)
        self.details_stack.addWidget(self.details_item)
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
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_name.sizePolicy().hasHeightForWidth())
        self.task_name.setSizePolicy(sizePolicy)
        self.task_name.setObjectName("task_name")
        self.horizontalLayout_4.addWidget(self.task_name)
        self.verticalLayout_11.addLayout(self.horizontalLayout_4)
        self.task_description = QtGui.QLabel(self.details_task)
        self.task_description.setMaximumSize(QtCore.QSize(350, 16777215))
        self.task_description.setTextFormat(QtCore.Qt.RichText)
        self.task_description.setWordWrap(True)
        self.task_description.setObjectName("task_description")
        self.verticalLayout_11.addWidget(self.task_description)
        self.task_settings_label = QtGui.QLabel(self.details_task)
        self.task_settings_label.setObjectName("task_settings_label")
        self.verticalLayout_11.addWidget(self.task_settings_label)
        self.task_settings = SettingsWidget(self.details_task)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.task_settings.sizePolicy().hasHeightForWidth())
        self.task_settings.setSizePolicy(sizePolicy)
        self.task_settings.setObjectName("task_settings")
        self.verticalLayout_11.addWidget(self.task_settings)
        self.details_stack.addWidget(self.details_task)
        self.details_please_select = QtGui.QWidget()
        self.details_please_select.setObjectName("details_please_select")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.details_please_select)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.please_select_an_item = QtGui.QLabel(self.details_please_select)
        self.please_select_an_item.setAlignment(QtCore.Qt.AlignCenter)
        self.please_select_an_item.setObjectName("please_select_an_item")
        self.verticalLayout_8.addWidget(self.please_select_an_item)
        self.details_stack.addWidget(self.details_please_select)
        self.verticalLayout_5.addWidget(self.details_stack)
        self.verticalLayout_9.addWidget(self.splitter)
        self.verticalLayout_4.addWidget(self.main_frame)
        self.progress_bar = QtGui.QProgressBar(self.main_ui_frame)
        self.progress_bar.setMaximumSize(QtCore.QSize(16777215, 10))
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout_4.addWidget(self.progress_bar)
        self.bottom_frame = QtGui.QFrame(self.main_ui_frame)
        self.bottom_frame.setMaximumSize(QtCore.QSize(16777215, 50))
        self.bottom_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.bottom_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.bottom_frame.setObjectName("bottom_frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.bottom_frame)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setContentsMargins(2, 0, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.delete_items = QtGui.QToolButton(self.bottom_frame)
        self.delete_items.setMaximumSize(QtCore.QSize(32, 32))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/trash.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_items.setIcon(icon)
        self.delete_items.setIconSize(QtCore.QSize(32, 32))
        self.delete_items.setObjectName("delete_items")
        self.horizontalLayout.addWidget(self.delete_items)
        self.expand_all = QtGui.QToolButton(self.bottom_frame)
        self.expand_all.setMaximumSize(QtCore.QSize(32, 32))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/expand.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.expand_all.setIcon(icon1)
        self.expand_all.setIconSize(QtCore.QSize(32, 32))
        self.expand_all.setObjectName("expand_all")
        self.horizontalLayout.addWidget(self.expand_all)
        self.collapse_all = QtGui.QToolButton(self.bottom_frame)
        self.collapse_all.setMaximumSize(QtCore.QSize(32, 32))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/contract.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.collapse_all.setIcon(icon2)
        self.collapse_all.setIconSize(QtCore.QSize(32, 32))
        self.collapse_all.setObjectName("collapse_all")
        self.horizontalLayout.addWidget(self.collapse_all)
        spacerItem4 = QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.progress_status_icon = QtGui.QLabel(self.bottom_frame)
        self.progress_status_icon.setMinimumSize(QtCore.QSize(20, 20))
        self.progress_status_icon.setMaximumSize(QtCore.QSize(20, 20))
        self.progress_status_icon.setText("")
        self.progress_status_icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/status_success.png"))
        self.progress_status_icon.setScaledContents(True)
        self.progress_status_icon.setObjectName("progress_status_icon")
        self.horizontalLayout.addWidget(self.progress_status_icon)
        self.progress_message = ProgressStatusLabel(self.bottom_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress_message.sizePolicy().hasHeightForWidth())
        self.progress_message.setSizePolicy(sizePolicy)
        self.progress_message.setObjectName("progress_message")
        self.horizontalLayout.addWidget(self.progress_message)
        self.validate = QtGui.QPushButton(self.bottom_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.validate.sizePolicy().hasHeightForWidth())
        self.validate.setSizePolicy(sizePolicy)
        self.validate.setObjectName("validate")
        self.horizontalLayout.addWidget(self.validate)
        self.publish = QtGui.QPushButton(self.bottom_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.publish.sizePolicy().hasHeightForWidth())
        self.publish.setSizePolicy(sizePolicy)
        self.publish.setObjectName("publish")
        self.horizontalLayout.addWidget(self.publish)
        self.close = QtGui.QPushButton(self.bottom_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close.sizePolicy().hasHeightForWidth())
        self.close.setSizePolicy(sizePolicy)
        self.close.setObjectName("close")
        self.horizontalLayout.addWidget(self.close)
        self.verticalLayout_4.addWidget(self.bottom_frame)
        self.main_stack.addWidget(self.main_ui_frame)
        self.verticalLayout_7.addWidget(self.main_stack)

        self.retranslateUi(Dialog)
        self.main_stack.setCurrentIndex(1)
        self.details_stack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Shotgun Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.large_drop_area_label.setText(QtGui.QApplication.translate("Dialog", "Drag and drop \n"
"files you want to publish.", None, QtGui.QApplication.UnicodeUTF8))
        self.text_below_item_tree.setText(QtGui.QApplication.translate("Dialog", "Drag and drop items here to add them. ", None, QtGui.QApplication.UnicodeUTF8))
        self.item_name.setText(QtGui.QApplication.translate("Dialog", "Item name", None, QtGui.QApplication.UnicodeUTF8))
        self.item_type.setText(QtGui.QApplication.translate("Dialog", "Item type", None, QtGui.QApplication.UnicodeUTF8))
        self.link_label.setText(QtGui.QApplication.translate("Dialog", "Link", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Thumbnail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.item_thumbnail.setToolTip(QtGui.QApplication.translate("Dialog", "Click to take a screenshot.", None, QtGui.QApplication.UnicodeUTF8))
        self.item_summary_label.setText(QtGui.QApplication.translate("Dialog", "Publish Summary", None, QtGui.QApplication.UnicodeUTF8))
        self.item_settings_label.setText(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.task_name.setText(QtGui.QApplication.translate("Dialog", "Task Name", None, QtGui.QApplication.UnicodeUTF8))
        self.task_description.setText(QtGui.QApplication.translate("Dialog", "task desc", None, QtGui.QApplication.UnicodeUTF8))
        self.task_settings_label.setText(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.please_select_an_item.setText(QtGui.QApplication.translate("Dialog", "Please select a single item in the list.", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_items.setToolTip(QtGui.QApplication.translate("Dialog", "Delete selected items", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_items.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.expand_all.setToolTip(QtGui.QApplication.translate("Dialog", "Expand all items", None, QtGui.QApplication.UnicodeUTF8))
        self.expand_all.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.collapse_all.setToolTip(QtGui.QApplication.translate("Dialog", "Collapse all items", None, QtGui.QApplication.UnicodeUTF8))
        self.collapse_all.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.progress_message.setText(QtGui.QApplication.translate("Dialog", "Progress message....", None, QtGui.QApplication.UnicodeUTF8))
        self.validate.setText(QtGui.QApplication.translate("Dialog", "Validate", None, QtGui.QApplication.UnicodeUTF8))
        self.publish.setText(QtGui.QApplication.translate("Dialog", "Publish", None, QtGui.QApplication.UnicodeUTF8))
        self.close.setText(QtGui.QApplication.translate("Dialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

from ..thumbnail import Thumbnail
from ..context_widget import ContextWidget
from ..progress_status_label import ProgressStatusLabel
from ..publish_tree_widget import PublishTreeWidget
from ..settings_widget import SettingsWidget
from ..drop_area import DropAreaFrame
from . import resources_rc
