# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog.ui'
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
from ..drop_area import DropAreaFrame
from ..thumbnail import Thumbnail
from ..settings_widget import SettingsWidget
from ..publish_tree_widget import PublishTreeWidget
from ..qtwidgets import ContextWidget
from ..qtwidgets import ElidedLabel
from ..custom_settings_widget import CustomSettingsWidget
from ..publish_description_edit import PublishDescriptionEdit

from  . import resources_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(709, 588)
        self.verticalLayout_7 = QVBoxLayout(Dialog)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.main_stack = QStackedWidget(Dialog)
        self.main_stack.setObjectName(u"main_stack")
        self.large_drop_area_frame = QWidget()
        self.large_drop_area_frame.setObjectName(u"large_drop_area_frame")
        self.verticalLayout_3 = QVBoxLayout(self.large_drop_area_frame)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.large_drop_area = DropAreaFrame(self.large_drop_area_frame)
        self.large_drop_area.setObjectName(u"large_drop_area")
        self.large_drop_area.setFrameShape(QFrame.StyledPanel)
        self.large_drop_area.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.large_drop_area)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalSpacer = QSpacerItem(20, 98, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(166, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_4, 1, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_5 = QLabel(self.large_drop_area)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(150, 150))
        self.label_5.setMaximumSize(QSize(150, 150))
        self.label_5.setPixmap(QPixmap(u":/tk_multi_publish2/icon_256.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_6.addWidget(self.label_5)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.large_drop_area_label = QLabel(self.large_drop_area)
        self.large_drop_area_label.setObjectName(u"large_drop_area_label")
        self.large_drop_area_label.setStyleSheet(u"QLabel {\n"
"    font-size: 24px;\n"
"}")
        self.large_drop_area_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.large_drop_area_label)

        self.verticalSpacer_5 = QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_5)

        self.label = QLabel(self.large_drop_area)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.verticalSpacer_6 = QSpacerItem(0, 16, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_6)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.drop_area_browse_file = QToolButton(self.large_drop_area)
        self.drop_area_browse_file.setObjectName(u"drop_area_browse_file")
        self.drop_area_browse_file.setMinimumSize(QSize(160, 85))
        self.drop_area_browse_file.setMaximumSize(QSize(150, 85))
        self.drop_area_browse_file.setFocusPolicy(Qt.NoFocus)
        icon = QIcon()
        icon.addFile(u":/tk_multi_publish2/file.png", QSize(), QIcon.Normal, QIcon.Off)
        self.drop_area_browse_file.setIcon(icon)
        self.drop_area_browse_file.setIconSize(QSize(32, 32))
        self.drop_area_browse_file.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_3.addWidget(self.drop_area_browse_file)

        self.horizontalSpacer_6 = QSpacerItem(12, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)

        self.drop_area_browse_seq = QToolButton(self.large_drop_area)
        self.drop_area_browse_seq.setObjectName(u"drop_area_browse_seq")
        self.drop_area_browse_seq.setMinimumSize(QSize(160, 85))
        self.drop_area_browse_seq.setMaximumSize(QSize(150, 85))
        self.drop_area_browse_seq.setFocusPolicy(Qt.NoFocus)
        icon1 = QIcon()
        icon1.addFile(u":/tk_multi_publish2/image_sequence.png", QSize(), QIcon.Normal, QIcon.Off)
        self.drop_area_browse_seq.setIcon(icon1)
        self.drop_area_browse_seq.setIconSize(QSize(32, 32))
        self.drop_area_browse_seq.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.horizontalLayout_3.addWidget(self.drop_area_browse_seq)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_4)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(8)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_7 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_7)

        self.drag_progress_message = QPushButton(self.large_drop_area)
        self.drag_progress_message.setObjectName(u"drag_progress_message")
        self.drag_progress_message.setFocusPolicy(Qt.NoFocus)
        icon2 = QIcon()
        icon2.addFile(u":/tk_multi_publish2/status_warning.png", QSize(), QIcon.Normal, QIcon.Off)
        self.drag_progress_message.setIcon(icon2)
        self.drag_progress_message.setIconSize(QSize(22, 22))
        self.drag_progress_message.setFlat(True)

        self.horizontalLayout_4.addWidget(self.drag_progress_message)

        self.horizontalSpacer_8 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.verticalLayout.setStretch(0, 10)
        self.verticalLayout.setStretch(6, 10)

        self.horizontalLayout_6.addLayout(self.verticalLayout)

        self.gridLayout_2.addLayout(self.horizontalLayout_6, 1, 1, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(179, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_5, 1, 2, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 213, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 2, 1, 1, 1)

        self.gridLayout_2.setRowStretch(0, 3)
        self.gridLayout_2.setRowStretch(2, 4)
        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(2, 1)

        self.verticalLayout_3.addWidget(self.large_drop_area)

        self.main_stack.addWidget(self.large_drop_area_frame)
        self.main_ui_frame = QWidget()
        self.main_ui_frame.setObjectName(u"main_ui_frame")
        self.verticalLayout_4 = QVBoxLayout(self.main_ui_frame)
        self.verticalLayout_4.setSpacing(2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.main_frame = QWidget(self.main_ui_frame)
        self.main_frame.setObjectName(u"main_frame")
        self.verticalLayout_9 = QVBoxLayout(self.main_frame)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.splitter = QSplitter(self.main_frame)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Horizontal)
        self.frame = DropAreaFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.items_tree = PublishTreeWidget(self.frame)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.items_tree.setHeaderItem(__qtreewidgetitem)
        self.items_tree.setObjectName(u"items_tree")
        self.items_tree.setAcceptDrops(True)
        self.items_tree.setDragEnabled(True)
        self.items_tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.items_tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.items_tree.header().setVisible(False)

        self.verticalLayout_2.addWidget(self.items_tree)

        self.text_below_item_tree = QLabel(self.frame)
        self.text_below_item_tree.setObjectName(u"text_below_item_tree")
        self.text_below_item_tree.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.text_below_item_tree)

        self.splitter.addWidget(self.frame)
        self.details_frame = QFrame(self.splitter)
        self.details_frame.setObjectName(u"details_frame")
        self.verticalLayout_5 = QVBoxLayout(self.details_frame)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.details_stack = QStackedWidget(self.details_frame)
        self.details_stack.setObjectName(u"details_stack")
        self.details_item = QWidget()
        self.details_item.setObjectName(u"details_item")
        self.verticalLayout_6 = QVBoxLayout(self.details_item)
        self.verticalLayout_6.setSpacing(8)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(8, 0, 8, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.item_icon = QLabel(self.details_item)
        self.item_icon.setObjectName(u"item_icon")
        self.item_icon.setMinimumSize(QSize(60, 60))
        self.item_icon.setMaximumSize(QSize(60, 60))
        self.item_icon.setScaledContents(True)
        self.item_icon.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.horizontalLayout_2.addWidget(self.item_icon)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.item_name = ElidedLabel(self.details_item)
        self.item_name.setObjectName(u"item_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.item_name.sizePolicy().hasHeightForWidth())
        self.item_name.setSizePolicy(sizePolicy1)
        self.item_name.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_12.addWidget(self.item_name)

        self.item_type = QLabel(self.details_item)
        self.item_type.setObjectName(u"item_type")
        sizePolicy1.setHeightForWidth(self.item_type.sizePolicy().hasHeightForWidth())
        self.item_type.setSizePolicy(sizePolicy1)
        self.item_type.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout_12.addWidget(self.item_type)

        self.verticalLayout_12.setStretch(0, 1)
        self.verticalLayout_12.setStretch(1, 2)

        self.horizontalLayout_2.addLayout(self.verticalLayout_12)

        self.horizontalLayout_2.setStretch(1, 10)

        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.item_divider_1 = QFrame(self.details_item)
        self.item_divider_1.setObjectName(u"item_divider_1")
        self.item_divider_1.setFrameShape(QFrame.HLine)
        self.item_divider_1.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_6.addWidget(self.item_divider_1)

        self.context_widget = ContextWidget(self.details_item)
        self.context_widget.setObjectName(u"context_widget")

        self.verticalLayout_6.addWidget(self.context_widget)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout_3.setVerticalSpacing(1)
        self.item_inherited_item_label = QLabel(self.details_item)
        self.item_inherited_item_label.setObjectName(u"item_inherited_item_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.item_inherited_item_label.sizePolicy().hasHeightForWidth())
        self.item_inherited_item_label.setSizePolicy(sizePolicy2)
        self.item_inherited_item_label.setStyleSheet(u"")
        self.item_inherited_item_label.setWordWrap(True)
        self.item_inherited_item_label.setIndent(5)
        self.item_inherited_item_label.setOpenExternalLinks(False)
        self.item_inherited_item_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse)

        self.gridLayout_3.addWidget(self.item_inherited_item_label, 2, 1, 1, 1)

        self.item_thumbnail_label = QLabel(self.details_item)
        self.item_thumbnail_label.setObjectName(u"item_thumbnail_label")

        self.gridLayout_3.addWidget(self.item_thumbnail_label, 0, 2, 1, 1)

        self.item_thumbnail = Thumbnail(self.details_item)
        self.item_thumbnail.setObjectName(u"item_thumbnail")
        self.item_thumbnail.setMinimumSize(QSize(160, 90))
        self.item_thumbnail.setMaximumSize(QSize(160, 90))
        self.item_thumbnail.setScaledContents(False)
        self.item_thumbnail.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.item_thumbnail, 1, 2, 1, 1)

        self.item_description_label = QLabel(self.details_item)
        self.item_description_label.setObjectName(u"item_description_label")

        self.gridLayout_3.addWidget(self.item_description_label, 0, 1, 1, 1)

        self.item_comments = PublishDescriptionEdit(self.details_item)
        self.item_comments.setObjectName(u"item_comments")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.item_comments.sizePolicy().hasHeightForWidth())
        self.item_comments.setSizePolicy(sizePolicy3)
        self.item_comments.setMinimumSize(QSize(0, 90))
        self.item_comments.setMaximumSize(QSize(16777215, 90))

        self.gridLayout_3.addWidget(self.item_comments, 1, 1, 1, 1)

        self.verticalLayout_6.addLayout(self.gridLayout_3)

        self.item_summary_label = QLabel(self.details_item)
        self.item_summary_label.setObjectName(u"item_summary_label")
        self.item_summary_label.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.verticalLayout_6.addWidget(self.item_summary_label)

        self.scrollArea = QScrollArea(self.details_item)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 408, 101))
        self.verticalLayout_10 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.item_summary = QLabel(self.scrollAreaWidgetContents)
        self.item_summary.setObjectName(u"item_summary")
        self.item_summary.setWordWrap(True)

        self.verticalLayout_10.addWidget(self.item_summary)

        self.expander_label = QLabel(self.scrollAreaWidgetContents)
        self.expander_label.setObjectName(u"expander_label")
        self.expander_label.setOpenExternalLinks(False)

        self.verticalLayout_10.addWidget(self.expander_label)

        self.verticalLayout_10.setStretch(1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_6.addWidget(self.scrollArea)

        self.item_settings_label = QLabel(self.details_item)
        self.item_settings_label.setObjectName(u"item_settings_label")
        self.item_settings_label.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.verticalLayout_6.addWidget(self.item_settings_label)

        self.item_settings = SettingsWidget(self.details_item)
        self.item_settings.setObjectName(u"item_settings")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.item_settings.sizePolicy().hasHeightForWidth())
        self.item_settings.setSizePolicy(sizePolicy4)

        self.verticalLayout_6.addWidget(self.item_settings)

        self.verticalLayout_6.setStretch(0, 1)
        self.verticalLayout_6.setStretch(1, 1)
        self.verticalLayout_6.setStretch(2, 1)
        self.verticalLayout_6.setStretch(3, 1)
        self.verticalLayout_6.setStretch(4, 1)
        self.verticalLayout_6.setStretch(5, 5)
        self.verticalLayout_6.setStretch(6, 1)
        self.verticalLayout_6.setStretch(7, 5)
        self.details_stack.addWidget(self.details_item)
        self.details_task = QWidget()
        self.details_task.setObjectName(u"details_task")
        self.verticalLayout_11 = QVBoxLayout(self.details_task)
        self.verticalLayout_11.setSpacing(8)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(8, 0, 8, 0)
        self.task_header_layout = QHBoxLayout()
        self.task_header_layout.setObjectName(u"task_header_layout")
        self.task_icon = QLabel(self.details_task)
        self.task_icon.setObjectName(u"task_icon")
        self.task_icon.setMinimumSize(QSize(60, 60))
        self.task_icon.setMaximumSize(QSize(60, 60))
        self.task_icon.setScaledContents(True)

        self.task_header_layout.addWidget(self.task_icon)

        self.task_name = QLabel(self.details_task)
        self.task_name.setObjectName(u"task_name")
        sizePolicy5 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.task_name.sizePolicy().hasHeightForWidth())
        self.task_name.setSizePolicy(sizePolicy5)

        self.task_header_layout.addWidget(self.task_name)

        self.verticalLayout_11.addLayout(self.task_header_layout)

        self.task_settings_scroll_area = QScrollArea(self.details_task)
        self.task_settings_scroll_area.setObjectName(u"task_settings_scroll_area")
        self.task_settings_scroll_area.setWidgetResizable(True)
        self.task_settings_parent = QWidget()
        self.task_settings_parent.setObjectName(u"task_settings_parent")
        self.task_settings_parent.setGeometry(QRect(0, 0, 408, 432))
        self.verticalLayout_13 = QVBoxLayout(self.task_settings_parent)
        self.verticalLayout_13.setSpacing(-1)
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.task_settings = CustomSettingsWidget(self.task_settings_parent)
        self.task_settings.setObjectName(u"task_settings")

        self.verticalLayout_13.addWidget(self.task_settings)

        self.task_settings_spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_13.addItem(self.task_settings_spacer)

        self.verticalLayout_13.setStretch(1, 10)
        self.task_settings_scroll_area.setWidget(self.task_settings_parent)

        self.verticalLayout_11.addWidget(self.task_settings_scroll_area)

        self.details_stack.addWidget(self.details_task)
        self.details_please_select = QWidget()
        self.details_please_select.setObjectName(u"details_please_select")
        self.verticalLayout_8 = QVBoxLayout(self.details_please_select)
        self.verticalLayout_8.setSpacing(8)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(8, 0, 8, 0)
        self.please_select_an_item = QLabel(self.details_please_select)
        self.please_select_an_item.setObjectName(u"please_select_an_item")
        self.please_select_an_item.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.please_select_an_item)

        self.details_stack.addWidget(self.details_please_select)
        self.details_multi_edit_not_supported = QWidget()
        self.details_multi_edit_not_supported.setObjectName(u"details_multi_edit_not_supported")
        self.verticalLayout_15 = QVBoxLayout(self.details_multi_edit_not_supported)
        self.verticalLayout_15.setSpacing(8)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(8, 0, 8, 0)
        self.label_2 = QLabel(self.details_multi_edit_not_supported)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_15.addWidget(self.label_2)

        self.details_stack.addWidget(self.details_multi_edit_not_supported)

        self.verticalLayout_5.addWidget(self.details_stack)

        self.splitter.addWidget(self.details_frame)

        self.verticalLayout_9.addWidget(self.splitter)

        self.verticalLayout_4.addWidget(self.main_frame)

        self.progress_bar = QProgressBar(self.main_ui_frame)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setMaximumSize(QSize(16777215, 10))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.verticalLayout_4.addWidget(self.progress_bar)

        self.bottom_frame = QFrame(self.main_ui_frame)
        self.bottom_frame.setObjectName(u"bottom_frame")
        self.bottom_frame.setMaximumSize(QSize(16777215, 50))
        self.bottom_frame.setFrameShape(QFrame.StyledPanel)
        self.bottom_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.bottom_frame)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(2, 8, 2, 2)
        self.button_container = QWidget(self.bottom_frame)
        self.button_container.setObjectName(u"button_container")
        self.horizontalLayout_5 = QHBoxLayout(self.button_container)
        self.horizontalLayout_5.setSpacing(4)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.browse = QToolButton(self.button_container)
        self.browse.setObjectName(u"browse")
        self.browse.setMaximumSize(QSize(32, 32))
        icon3 = QIcon()
        icon3.addFile(u":/tk_multi_publish2/browse_menu.png", QSize(), QIcon.Normal, QIcon.Off)
        self.browse.setIcon(icon3)
        self.browse.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.browse)

        self.refresh = QToolButton(self.button_container)
        self.refresh.setObjectName(u"refresh")
        self.refresh.setMaximumSize(QSize(32, 32))
        icon4 = QIcon()
        icon4.addFile(u":/tk_multi_publish2/refresh.png", QSize(), QIcon.Normal, QIcon.Off)
        self.refresh.setIcon(icon4)
        self.refresh.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.refresh)

        self.delete_items = QToolButton(self.button_container)
        self.delete_items.setObjectName(u"delete_items")
        self.delete_items.setMaximumSize(QSize(32, 32))
        icon5 = QIcon()
        icon5.addFile(u":/tk_multi_publish2/trash.png", QSize(), QIcon.Normal, QIcon.Off)
        self.delete_items.setIcon(icon5)
        self.delete_items.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.delete_items)

        self.expand_all = QToolButton(self.button_container)
        self.expand_all.setObjectName(u"expand_all")
        self.expand_all.setMaximumSize(QSize(32, 32))
        icon6 = QIcon()
        icon6.addFile(u":/tk_multi_publish2/expand.png", QSize(), QIcon.Normal, QIcon.Off)
        self.expand_all.setIcon(icon6)
        self.expand_all.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.expand_all)

        self.collapse_all = QToolButton(self.button_container)
        self.collapse_all.setObjectName(u"collapse_all")
        self.collapse_all.setMaximumSize(QSize(32, 32))
        icon7 = QIcon()
        icon7.addFile(u":/tk_multi_publish2/contract.png", QSize(), QIcon.Normal, QIcon.Off)
        self.collapse_all.setIcon(icon7)
        self.collapse_all.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.collapse_all)

        self.help = QToolButton(self.button_container)
        self.help.setObjectName(u"help")
        self.help.setMinimumSize(QSize(32, 32))
        self.help.setMaximumSize(QSize(32, 32))
        icon8 = QIcon()
        icon8.addFile(u":/tk_multi_publish2/help.png", QSize(), QIcon.Normal, QIcon.Off)
        self.help.setIcon(icon8)
        self.help.setIconSize(QSize(32, 32))

        self.horizontalLayout_5.addWidget(self.help)

        self.horizontalLayout.addWidget(self.button_container)

        self.horizontalSpacer = QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.progress_status_icon = QLabel(self.bottom_frame)
        self.progress_status_icon.setObjectName(u"progress_status_icon")
        self.progress_status_icon.setMinimumSize(QSize(20, 20))
        self.progress_status_icon.setMaximumSize(QSize(20, 20))
        self.progress_status_icon.setPixmap(QPixmap(u":/tk_multi_publish2/status_success.png"))
        self.progress_status_icon.setScaledContents(True)

        self.horizontalLayout.addWidget(self.progress_status_icon)

        self.progress_message = ProgressStatusLabel(self.bottom_frame)
        self.progress_message.setObjectName(u"progress_message")
        sizePolicy6 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.progress_message.sizePolicy().hasHeightForWidth())
        self.progress_message.setSizePolicy(sizePolicy6)

        self.horizontalLayout.addWidget(self.progress_message)

        self.stop_processing = QToolButton(self.bottom_frame)
        self.stop_processing.setObjectName(u"stop_processing")
        icon9 = QIcon()
        icon9.addFile(u":/tk_multi_publish2/cross.png", QSize(), QIcon.Normal, QIcon.Off)
        self.stop_processing.setIcon(icon9)
        self.stop_processing.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.stop_processing)

        self.validate = QPushButton(self.bottom_frame)
        self.validate.setObjectName(u"validate")
        sizePolicy7 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.validate.sizePolicy().hasHeightForWidth())
        self.validate.setSizePolicy(sizePolicy7)

        self.horizontalLayout.addWidget(self.validate)

        self.publish = QPushButton(self.bottom_frame)
        self.publish.setObjectName(u"publish")
        sizePolicy7.setHeightForWidth(self.publish.sizePolicy().hasHeightForWidth())
        self.publish.setSizePolicy(sizePolicy7)

        self.horizontalLayout.addWidget(self.publish)

        self.close = QPushButton(self.bottom_frame)
        self.close.setObjectName(u"close")
        sizePolicy7.setHeightForWidth(self.close.sizePolicy().hasHeightForWidth())
        self.close.setSizePolicy(sizePolicy7)

        self.horizontalLayout.addWidget(self.close)

        self.verticalLayout_4.addWidget(self.bottom_frame)

        self.main_stack.addWidget(self.main_ui_frame)

        self.verticalLayout_7.addWidget(self.main_stack)

        QWidget.setTabOrder(self.validate, self.publish)
        QWidget.setTabOrder(self.publish, self.items_tree)
        QWidget.setTabOrder(self.items_tree, self.close)
        QWidget.setTabOrder(self.close, self.stop_processing)
        QWidget.setTabOrder(self.stop_processing, self.scrollArea)

        self.retranslateUi(Dialog)

        self.main_stack.setCurrentIndex(1)
        self.details_stack.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Flow Production Tracking Publish", None))
#if QT_CONFIG(accessibility)
        Dialog.setAccessibleName(QCoreApplication.translate("Dialog", u"publish dialog", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.main_stack.setAccessibleName(QCoreApplication.translate("Dialog", u"stackedwidget", None))
#endif // QT_CONFIG(accessibility)
        self.label_5.setText("")
        self.large_drop_area_label.setText(QCoreApplication.translate("Dialog", u"Drag and drop files or folders here", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Or, if you prefer...", None))
#if QT_CONFIG(tooltip)
        self.drop_area_browse_file.setToolTip(QCoreApplication.translate("Dialog", u"Browse files to publish", None))
#endif // QT_CONFIG(tooltip)
        self.drop_area_browse_file.setText(QCoreApplication.translate("Dialog", u"Browse files to publish\n"
"    ", None))
#if QT_CONFIG(tooltip)
        self.drop_area_browse_seq.setToolTip(QCoreApplication.translate("Dialog", u"Browse sequences to publish", None))
#endif // QT_CONFIG(tooltip)
        self.drop_area_browse_seq.setText(QCoreApplication.translate("Dialog", u"Browse folders to publish\n"
"image sequences", None))
        self.drag_progress_message.setText(QCoreApplication.translate("Dialog", u"Click for more info...", None))
#if QT_CONFIG(accessibility)
        self.main_ui_frame.setAccessibleName(QCoreApplication.translate("Dialog", u"Main publish frame", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.main_frame.setAccessibleName(QCoreApplication.translate("Dialog", u"Upper frame", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.splitter.setAccessibleName(QCoreApplication.translate("Dialog", u"splitter", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.frame.setAccessibleName(QCoreApplication.translate("Dialog", u"tree frame", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.items_tree.setAccessibleName(QCoreApplication.translate("Dialog", u"collected items tree", None))
#endif // QT_CONFIG(accessibility)
        self.text_below_item_tree.setText(QCoreApplication.translate("Dialog", u"Drag and drop items here to add them. ", None))
#if QT_CONFIG(accessibility)
        self.details_frame.setAccessibleName(QCoreApplication.translate("Dialog", u"details frame", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.details_stack.setAccessibleName(QCoreApplication.translate("Dialog", u"details stacked widget", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.details_item.setAccessibleName(QCoreApplication.translate("Dialog", u"item details", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.item_icon.setAccessibleName(QCoreApplication.translate("Dialog", u"item icon", None))
#endif // QT_CONFIG(accessibility)
        self.item_icon.setText("")
        self.item_name.setText(QCoreApplication.translate("Dialog", u"Item name", None))
        self.item_type.setText(QCoreApplication.translate("Dialog", u"Item type", None))
#if QT_CONFIG(accessibility)
        self.item_divider_1.setAccessibleName(QCoreApplication.translate("Dialog", u"divider", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.context_widget.setAccessibleName(QCoreApplication.translate("Dialog", u"context picker widget", None))
#endif // QT_CONFIG(accessibility)
        self.item_inherited_item_label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-size:10pt;\">Inherited from: test</span></p></body></html>", None))
        self.item_thumbnail_label.setText(QCoreApplication.translate("Dialog", u"Thumbnail:", None))
#if QT_CONFIG(tooltip)
        self.item_thumbnail.setToolTip(QCoreApplication.translate("Dialog", u"Click to take a screenshot.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.item_thumbnail.setAccessibleName(QCoreApplication.translate("Dialog", u"item thumbnail", None))
#endif // QT_CONFIG(accessibility)
        self.item_thumbnail.setText("")
        self.item_description_label.setText(QCoreApplication.translate("Dialog", u"Description:", None))
#if QT_CONFIG(accessibility)
        self.item_comments.setAccessibleName(QCoreApplication.translate("Dialog", u"item description", None))
#endif // QT_CONFIG(accessibility)
        self.item_summary_label.setText(QCoreApplication.translate("Dialog", u"Summary:", None))
#if QT_CONFIG(accessibility)
        self.scrollArea.setAccessibleName(QCoreApplication.translate("Dialog", u"summary scroll area", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.scrollAreaWidgetContents.setAccessibleName(QCoreApplication.translate("Dialog", u"summary contents holder", None))
#endif // QT_CONFIG(accessibility)
        self.item_summary.setText("")
#if QT_CONFIG(accessibility)
        self.expander_label.setAccessibleName(QCoreApplication.translate("Dialog", u"expander label", None))
#endif // QT_CONFIG(accessibility)
        self.expander_label.setText("")
#if QT_CONFIG(accessibility)
        self.item_settings_label.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.item_settings_label.setText(QCoreApplication.translate("Dialog", u"Settings:", None))
#if QT_CONFIG(accessibility)
        self.item_settings.setAccessibleName(QCoreApplication.translate("Dialog", u"item settings", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.details_task.setAccessibleName(QCoreApplication.translate("Dialog", u"task details", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.task_icon.setAccessibleName(QCoreApplication.translate("Dialog", u"task icon", None))
#endif // QT_CONFIG(accessibility)
        self.task_icon.setText("")
        self.task_name.setText(QCoreApplication.translate("Dialog", u"Task Name", None))
#if QT_CONFIG(accessibility)
        self.task_settings_scroll_area.setAccessibleName(QCoreApplication.translate("Dialog", u"task settings scroll area", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.task_settings_parent.setAccessibleName(QCoreApplication.translate("Dialog", u"task settings parent", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.task_settings.setAccessibleName(QCoreApplication.translate("Dialog", u"task settings", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.details_please_select.setAccessibleName(QCoreApplication.translate("Dialog", u"unselected details", None))
#endif // QT_CONFIG(accessibility)
        self.please_select_an_item.setText(QCoreApplication.translate("Dialog", u"Please select tasks of the same type or a single item.", None))
#if QT_CONFIG(accessibility)
        self.details_multi_edit_not_supported.setAccessibleName(QCoreApplication.translate("Dialog", u"non multi edit details", None))
#endif // QT_CONFIG(accessibility)
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Multiple selection not supported on tasks of this type.\n"
"Please select a single task.", None))
#if QT_CONFIG(accessibility)
        self.bottom_frame.setAccessibleName(QCoreApplication.translate("Dialog", u"Bottom frame", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.button_container.setAccessibleName(QCoreApplication.translate("Dialog", u"button container", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(tooltip)
        self.browse.setToolTip(QCoreApplication.translate("Dialog", u"<p>Click this button to browse files for publishing. You can also click and hold the button to show the full browsing menu which includes an option to browse folders to publish image sequences.</p>", None))
#endif // QT_CONFIG(tooltip)
        self.browse.setText(QCoreApplication.translate("Dialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.refresh.setToolTip(QCoreApplication.translate("Dialog", u"Refresh", None))
#endif // QT_CONFIG(tooltip)
        self.refresh.setText(QCoreApplication.translate("Dialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.delete_items.setToolTip(QCoreApplication.translate("Dialog", u"Delete selected items", None))
#endif // QT_CONFIG(tooltip)
        self.delete_items.setText(QCoreApplication.translate("Dialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.expand_all.setToolTip(QCoreApplication.translate("Dialog", u"Expand all items", None))
#endif // QT_CONFIG(tooltip)
        self.expand_all.setText(QCoreApplication.translate("Dialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.collapse_all.setToolTip(QCoreApplication.translate("Dialog", u"Collapse all items", None))
#endif // QT_CONFIG(tooltip)
        self.collapse_all.setText(QCoreApplication.translate("Dialog", u"...", None))
#if QT_CONFIG(tooltip)
        self.help.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Open documentation for the publish workflow.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.help.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.progress_status_icon.setText("")
        self.progress_message.setText(QCoreApplication.translate("Dialog", u"Progress message....", None))
#if QT_CONFIG(tooltip)
        self.stop_processing.setToolTip(QCoreApplication.translate("Dialog", u"Stop Processing", None))
#endif // QT_CONFIG(tooltip)
        self.stop_processing.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.validate.setText(QCoreApplication.translate("Dialog", u"Validate", None))
        self.publish.setText(QCoreApplication.translate("Dialog", u"Publish", None))
        self.close.setText(QCoreApplication.translate("Dialog", u"Close", None))
    # retranslateUi
