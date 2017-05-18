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

from .ui.context_editor_widget import Ui_ContextWidget

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

        # set up the UI
        self.ui = Ui_ContextWidget()
        self.ui.setupUi(self)






    def set_up(self, task_manager):
        """
        Does the post-init setup of the widget
        """
        self.ui.context_link.set_bg_task_manager(task_manager)

    def set_context(self, context):
        """
        Register a context with the widget
        """
        logger.debug("Setting up %s for context %s" % (self, context))
        entity = context.entity or context.project or None
        #self._entity_combo_box.set_entity(entity)
        #self._task_combo_box.set_task(entity, context.task)
        self.ui.context_link.setText(entity.get("name", "Unnamed"))

    # def _on_entity_update(self):
    #     """
    #     Fires when the user selects something in the entity tree view combo
    #     """
    #     # get sg data from the combo box
    #     sg_data = self._entity_combo_box.get_selected_entity()
    #
    #     if sg_data:
    #         ctx = self._bundle.sgtk.context_from_entity(
    #             sg_data["ref"]["value"]["type"],
    #             sg_data["ref"]["value"]["id"]
    #         )
    #         self.context_changed.emit(ctx)
    #
    # def _on_task_update(self):
    #     """
    #     Fires when a task is clicked in the dropdown
    #     """
    #     # get sg data from the combo box
    #     task_id = self._task_combo_box.get_selected_task_id()
    #
    #     if task_id:
    #         ctx = self._bundle.sgtk.context_from_entity("Task", task_id)
    #         self.context_changed.emit(ctx)
