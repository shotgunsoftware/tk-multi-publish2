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
        Dialog.resize(828, 613)
        self.verticalLayout_7 = QtGui.QVBoxLayout(Dialog)
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
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.splitter = QtGui.QSplitter(self.main_ui_frame)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.frame = DropAreaFrame(self.splitter)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
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
        self.details_frame = QtGui.QFrame(self.splitter)
        self.details_frame.setObjectName("details_frame")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.details_frame)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.details_stack = QtGui.QStackedWidget(self.details_frame)
        self.details_stack.setObjectName("details_stack")
        self.details_summary = QtGui.QWidget()
        self.details_summary.setObjectName("details_summary")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.details_summary)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.summary_icon = QtGui.QLabel(self.details_summary)
        self.summary_icon.setMinimumSize(QtCore.QSize(60, 60))
        self.summary_icon.setMaximumSize(QtCore.QSize(60, 60))
        self.summary_icon.setText("")
        self.summary_icon.setScaledContents(True)
        self.summary_icon.setObjectName("summary_icon")
        self.horizontalLayout_2.addWidget(self.summary_icon)
        self.verticalLayout_12 = QtGui.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.item_name = QtGui.QLabel(self.details_summary)
        self.item_name.setObjectName("item_name")
        self.verticalLayout_12.addWidget(self.item_name)
        self.item_type = QtGui.QLabel(self.details_summary)
        self.item_type.setObjectName("item_type")
        self.verticalLayout_12.addWidget(self.item_type)
        self.horizontalLayout_2.addLayout(self.verticalLayout_12)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.summary_divider = QtGui.QFrame(self.details_summary)
        self.summary_divider.setFrameShape(QtGui.QFrame.HLine)
        self.summary_divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.summary_divider.setObjectName("summary_divider")
        self.verticalLayout_6.addWidget(self.summary_divider)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtGui.QLabel(self.details_summary)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.summary_context = QtGui.QLabel(self.details_summary)
        self.summary_context.setObjectName("summary_context")
        self.horizontalLayout_5.addWidget(self.summary_context)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_2 = QtGui.QLabel(self.details_summary)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_6.addWidget(self.label_2)
        self.summary_thumbnail = Thumbnail(self.details_summary)
        self.summary_thumbnail.setMinimumSize(QtCore.QSize(160, 90))
        self.summary_thumbnail.setMaximumSize(QtCore.QSize(160, 90))
        self.summary_thumbnail.setText("")
        self.summary_thumbnail.setScaledContents(True)
        self.summary_thumbnail.setObjectName("summary_thumbnail")
        self.horizontalLayout_6.addWidget(self.summary_thumbnail)
        self.verticalLayout_6.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_3 = QtGui.QLabel(self.details_summary)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_7.addWidget(self.label_3)
        self.summary_comments = QtGui.QPlainTextEdit(self.details_summary)
        self.summary_comments.setObjectName("summary_comments")
        self.horizontalLayout_7.addWidget(self.summary_comments)
        self.verticalLayout_6.addLayout(self.horizontalLayout_7)
        self.item_divider = QtGui.QFrame(self.details_summary)
        self.item_divider.setFrameShape(QtGui.QFrame.HLine)
        self.item_divider.setFrameShadow(QtGui.QFrame.Sunken)
        self.item_divider.setObjectName("item_divider")
        self.verticalLayout_6.addWidget(self.item_divider)
        self.item_settings_label = QtGui.QLabel(self.details_summary)
        self.item_settings_label.setObjectName("item_settings_label")
        self.verticalLayout_6.addWidget(self.item_settings_label)
        self.item_settings = SettingsWidget(self.details_summary)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.item_settings.sizePolicy().hasHeightForWidth())
        self.item_settings.setSizePolicy(sizePolicy)
        self.item_settings.setObjectName("item_settings")
        self.verticalLayout_6.addWidget(self.item_settings)
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
        self.verticalLayout_5.addWidget(self.details_stack)
        self.verticalLayout_4.addWidget(self.splitter)
        self.progress_widget = ProgressWidget(self.main_ui_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress_widget.sizePolicy().hasHeightForWidth())
        self.progress_widget.setSizePolicy(sizePolicy)
        self.progress_widget.setObjectName("progress_widget")
        self.verticalLayout_4.addWidget(self.progress_widget)
        self.bottom_frame = QtGui.QFrame(self.main_ui_frame)
        self.bottom_frame.setMaximumSize(QtCore.QSize(16777215, 50))
        self.bottom_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.bottom_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.bottom_frame.setObjectName("bottom_frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.bottom_frame)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.options = QtGui.QPushButton(self.bottom_frame)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/tick.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.options.setIcon(icon)
        self.options.setObjectName("options")
        self.horizontalLayout.addWidget(self.options)
        spacerItem4 = QtGui.QSpacerItem(638, 11, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.validate = QtGui.QPushButton(self.bottom_frame)
        self.validate.setObjectName("validate")
        self.horizontalLayout.addWidget(self.validate)
        self.publish = QtGui.QPushButton(self.bottom_frame)
        self.publish.setObjectName("publish")
        self.horizontalLayout.addWidget(self.publish)
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
        self.item_name.setText(QtGui.QApplication.translate("Dialog", "Item name", None, QtGui.QApplication.UnicodeUTF8))
        self.item_type.setText(QtGui.QApplication.translate("Dialog", "Item type", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Publishing to", None, QtGui.QApplication.UnicodeUTF8))
        self.summary_context.setText(QtGui.QApplication.translate("Dialog", "Current Context", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Thumbnail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.item_settings_label.setText(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.task_name.setText(QtGui.QApplication.translate("Dialog", "Task Name", None, QtGui.QApplication.UnicodeUTF8))
        self.task_description.setText(QtGui.QApplication.translate("Dialog", "task desc", None, QtGui.QApplication.UnicodeUTF8))
        self.task_settings_label.setText(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.validate.setText(QtGui.QApplication.translate("Dialog", "Validate", None, QtGui.QApplication.UnicodeUTF8))
        self.publish.setText(QtGui.QApplication.translate("Dialog", "Publish", None, QtGui.QApplication.UnicodeUTF8))

from ..publish_tree_widget import PublishTreeWidget
from ..settings_widget import SettingsWidget
from ..progress_widget import ProgressWidget
from ..drop_area import DropAreaFrame
from ..thumbnail import Thumbnail
from . import resources_rc
