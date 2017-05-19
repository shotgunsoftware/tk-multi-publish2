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

shotgun_fields = sgtk.platform.import_framework(
    "tk-framework-qtwidgets", "shotgun_fields")

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

        # we will do a bg query that requires an id to catch results
        self._schema_query_id = None

        self._task_manager = None

        # set up the UI
        self.ui = Ui_ContextWidget()
        self.ui.setupUi(self)

    def set_up(self, task_manager):
        """
        Does the post-init setup of the widget
        """

        self._task_manager = task_manager

        self._fields_manager = shotgun_fields.ShotgunFieldManager(
            self, bg_task_manager=task_manager)
        self._fields_manager.initialized.connect(self._populate_ui)
        self._fields_manager.initialize()

    def _populate_ui(self):

        publisher = sgtk.platform.current_bundle()
        project = publisher.context.project

        # remove the placeholder labels
        self.ui.context_layout.removeWidget(self.ui.link_placeholder)
        self.ui.link_placeholder.hide()
        self.ui.context_layout.removeWidget(self.ui.task_placeholder)
        self.ui.task_placeholder.hide()

        # get entity editor widgets for link and task
        self._link_edit = self._fields_manager.create_widget(
            "PublishedFile",
            "entity",
            parent=self
        )
        self._link_edit.setMinimumWidth(155)


        self._link_edit.editor_widget.set_placeholder_text("Search Links...")
        self._link_edit.show_editor()

        self._task_edit = self._fields_manager.create_widget(
            "PublishedFile",
            "task",
            parent=self
        )
        self._task_edit.setMinimumWidth(155)
        self._task_edit.editor_widget.set_placeholder_text("Search Tasks...")
        self._task_edit.show_editor()

        # add the widgets to the UI
        self.ui.context_layout.addWidget(self._link_edit)
        self.ui.context_layout.addWidget(self._task_edit)
        self.ui.context_layout.addStretch()
        self.ui.context_layout.setStretch(0, 1)
        self.ui.context_layout.setStretch(1, 1)
        self.ui.context_layout.setStretch(2, 2)

        # limit the task search
        filters = [["project", "is", project]] if project else []
        task_dict = {"Task": filters}
        self._task_edit.editor_widget.set_searchable_entity_types(task_dict)

        # do a bg query to limit the link edit entity types
        self._query_valid_entity_types(self._task_manager)

    def _query_valid_entity_types(self, task_manager):
        """
        Query Shotgun for valid entity types for the PublishedFile.entity field
        """

        # we need to limit the search completer to entity types that are valid
        # for ``PublishedFile.entity`` field links. To do this, query the
        # shotgun schema to get a list of these entity types. We use the current
        # project schema if we're in a project. We do this as a background query
        # via the supplied task manager.
        publisher = sgtk.platform.current_bundle()
        project = publisher.context.project

        logger.debug(
            "Querying PublishedFile.entity schema for entity types for project "
            "%s..." % (project,)
        )

        # connect to the task manager signals so that we can get the results
        task_manager.task_completed.connect(self._on_task_completed)
        task_manager.task_failed.connect(self._on_task_failed)

        self._schema_query_id = task_manager.add_task(
            publisher.shotgun.schema_field_read,
            task_args=["PublishedFile"],
            task_kwargs=dict(
                field_name="entity",
                project_entity=project
            )
        )

    def _on_link_edit_clicked(self, url):
        print "LINK: " + str(url)
        if url == "#edit_link":
            self._link_edit.show_editor()

    def _on_task_edit_clicked(self, url):
        print "LINK: " + str(url)
        if url == "#edit_task":
            self._task_edit.show_editor()

    def _on_task_completed(self, task_id, group, result):
        """
        Handle the results of our published file entity field schema query.
        """

        if task_id != self._schema_query_id:
            # not interested in this task
            return

        published_file_entity_schema = result

        # drill down into the schema to retrieve the valid types for the field.
        # this is ugly, but will ensure we get a list no matter what
        entity_types = published_file_entity_schema. \
            get("entity", {}). \
            get("properties", {}). \
            get("valid_types", {}). \
            get("value", [])

        # always include Project
        entity_types.append("Project")

        logger.debug(
            "Limiting context link completer to these entities: %s" %
            (entity_types,)
        )

        # construct a dictionary that the search widget expects for
        # filtering. This is a dictionary with the entity types as keys and
        # values a list of search filters. We don't have any filters, so we
        # just use empty list.
        entity_types_dict = dict((k, []) for k in entity_types)

        logger.debug(
            "Setting searchable entity types to: %s" % (entity_types_dict,))

        # now update the types for the completer
        self._link_edit.editor_widget.set_searchable_entity_types(entity_types_dict)

    def _on_task_failed(self, task_id, group, message, traceback_str):
        """
        If the schema query fails, add a log warning. It's not catastrophic, but
        it shouldn't fail, so we need to make a record of it.
        """

        if task_id != self._schema_query_id:
            # not interested in this task
            return

        logger.warn(
            "Unable to query valid entity types for PublishedFile.entity."
            "Error Message: %s.\n%s" % (message, traceback_str)
        )

    def set_context(self, context):
        """
        Register a context with the widget
        """
        logger.debug("Setting up %s for context %s" % (self, context))
        entity = context.entity or context.project or None

        self._link_edit.set_value(entity)
        self._link_edit.show_display()

        if context.task:
            self._task_edit.set_value(context.task)
            self._task_edit.show_display()

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
