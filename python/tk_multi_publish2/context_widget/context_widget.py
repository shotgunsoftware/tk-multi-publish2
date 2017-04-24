# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
from sgtk.platform.qt import QtCore, QtGui
import sgtk
from .task_combo_box import TaskComboBox
from .entity_combo_box import EntityComboBox

logger = sgtk.platform.get_logger(__name__)


class ContextWidget(QtGui.QWidget):
    """
    Widget which represents the current context in the form
    of combo boxes which lets the user change the context.

    Emits a context_changed signal when the user selects a new context
    """

    # emitted when a settings button is clicked on a node
    context_changed = QtCore.Signal(object)


    def __init__(self, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(ContextWidget, self).__init__(parent)

        self._bundle = sgtk.platform.current_bundle()

        self._grid_layout = QtGui.QGridLayout(self)
        self._grid_layout.setContentsMargins(4, 4, 4, 4)
        self._grid_layout.setSpacing(4)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setObjectName("grid_layout")

        self._entity_combo_box = EntityComboBox(self)
        self._entity_combo_box.setObjectName("entity_combo_box")
        self._grid_layout.addWidget(self._entity_combo_box, 0, 0, 1, 2)

        self._task_combo_box= TaskComboBox(self)
        self._task_combo_box.setObjectName("task_combo_box")
        self._grid_layout.addWidget(self._task_combo_box, 1, 0, 1, 1)

        self._favorites_button = QtGui.QToolButton(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._favorites_button.sizePolicy().hasHeightForWidth())
        self._favorites_button.setSizePolicy(sizePolicy)
        self._favorites_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/tk_multi_publish2/star.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._favorites_button.setIcon(icon)
        self._favorites_button.setIconSize(QtCore.QSize(20, 20))
        self._favorites_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        self._favorites_button.setObjectName("favorites_button")
        self._grid_layout.addWidget(self._favorites_button, 1, 1, 1, 1)

        self._entity_combo_box.currentIndexChanged.connect(self._on_entity_update)
        self._task_combo_box.activated.connect(self._on_task_update)

    def set_up(self, task_manager):
        """
        Does the post-init setup of the widget
        """
        self._entity_combo_box.set_up(task_manager)
        self._task_combo_box.set_up(task_manager)

    def set_context(self, context):
        """
        Register a context with the widget
        """
        logger.debug("Setting up %s for context %s" % (self, context))
        entity = context.entity or context.project or None
        self._entity_combo_box.set_entity(entity)
        self._task_combo_box.set_task(entity, context.task)

    def _on_entity_update(self):
        """
        Fires when the user selects something in the entity tree view combo
        """
        # get sg data from the combo box
        sg_data = self._entity_combo_box.get_selected_entity()

        if sg_data:
            ctx = self._bundle.sgtk.context_from_entity(
                sg_data["ref"]["value"]["type"],
                sg_data["ref"]["value"]["id"]
            )
            self.context_changed.emit(ctx)

    def _on_task_update(self):
        """
        Fires when a task is clicked in the dropdown
        """
        # get sg data from the combo box
        task_id = self._task_combo_box.get_selected_task_id()

        if task_id:
            ctx = self._bundle.sgtk.context_from_entity("Task", task_id)
            self.context_changed.emit(ctx)
