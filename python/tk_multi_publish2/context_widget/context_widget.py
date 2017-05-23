# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import copy
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from .ui.context_editor_widget import Ui_ContextWidget

# framework imports
shotgun_fields = sgtk.platform.import_framework(
    "tk-framework-qtwidgets", "shotgun_fields")

shotgun_menus = sgtk.platform.import_framework(
    "tk-framework-qtwidgets", "shotgun_menus")

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals")

settings = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "settings")

logger = sgtk.platform.get_logger(__name__)

# TODO:
# related tasks for entity context
# tooltips updated
# code cleanup
# manual toggle search methods
# only add recent after publishing
class ContextWidget(QtGui.QWidget):
    """
    Widget which represents the current context and allows the user to search
    for a different context via search completer. A menu is also provided for
    recent contexts as well as tasks assigned to the user.

    Emits a context_changed signal when the user selects a new context
    """

    # emitted when a settings button is clicked on a node
    context_changed = QtCore.Signal(object)

    def __init__(self, parent):
        """
        Initialize the widget

        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(ContextWidget, self).__init__(parent)

        self._bundle = sgtk.platform.current_bundle()

        # get instance of user settings to save/restore values across sessions
        self._settings = settings.UserSettings(self._bundle)

        # the key we'll use to store/retrieve recent contexts via user settings
        self._settings_recent_contexts_key = "%s_recent_contexts" % (
            self._bundle.name,)

        # we will do a bg query that requires an id to catch results
        self._schema_query_id = None

        # another query to get all tasks assigned to the current user
        self._my_tasks_query_id = None

        # keep a handle on the current context
        self._context = None

        # menu for recent and user contexts
        self._task_menu = shotgun_menus.ShotgunMenu(self)
        self._task_menu.setObjectName("context_menu")
        self._task_menu.addAction("Loading...")

        # keep a handle on all actions created. the my tasks menu will be
        # constant, but the recents menu will be dynamic. so we build the menu
        # just before it is shown. these lists hold the QActions for each
        # group of contexts to show in the menu
        self._menu_actions = {
            "My Tasks": [],
            "Recent": []
        }

        # set up the UI
        self.ui = Ui_ContextWidget()
        self.ui.setupUi(self)

    def eventFilter(self, widget, event):

        key_event = QtCore.QEvent.KeyPress
        click_event = QtCore.QEvent.MouseButtonRelease

        if widget == self.ui.task_display:

            if event.type() == click_event:
                self._on_task_search_toggled(True)
                self.ui.task_search_btn.setChecked(True)
                self.ui.task_search_btn.setDown(True)
                return True

        if widget == self.ui.task_search:

            if event.type() == key_event:

                if event.key() == QtCore.Qt.Key_Escape:
                    self._on_task_search_toggled(False)
                    self.ui.task_search_btn.setChecked(False)
                    self.ui.task_search_btn.setDown(False)
                    return True
                elif event.key() in [
                    QtCore.Qt.Key_Tab,
                    QtCore.Qt.Key_Return,
                    QtCore.Qt.Key_Enter,
                ]:
                    result = self.ui.task_search.completer().get_first_result()
                    if result:
                        self._on_entity_activated(
                            result["type"],
                            result["id"],
                            result["name"]
                        )

        if widget == self.ui.link_display:

            if event.type() == click_event:
                self._on_link_search_toggled(True)
                self.ui.link_search_btn.setChecked(True)
                self.ui.link_search_btn.setDown(True)
                return True

        if widget == self.ui.link_search:

            if event.type() == key_event:

                if event.key() == QtCore.Qt.Key_Escape:
                    self._on_link_search_toggled(False)
                    self.ui.link_search_btn.setChecked(False)
                    self.ui.link_search_btn.setDown(False)
                    return True
                elif event.key() in [
                    QtCore.Qt.Key_Tab,
                    QtCore.Qt.Key_Return,
                    QtCore.Qt.Key_Enter,
                ]:
                    result = self.ui.link_search.completer().get_first_result()
                    if result:
                        self._on_entity_activated(
                            result["type"],
                            result["id"],
                            result["name"]
                        )

        return False

    def save_recent_contexts(self):
        """
        Should be called by the parent widget, typically when the dialog closes,
        to ensure the recent contexts are saved to disk when closing.
        """

        # build a list of serialized recent contexts. we grab all the QActions
        #
        serialized_contexts = []
        for recent_action in self._menu_actions["Recent"]:
            recent_context = recent_action.data()
            serialized_contexts.append(recent_context.serialize())

        # store the recent contexts on disk. the scope is per-project
        self._settings.store(
            self._settings_recent_contexts_key,
            serialized_contexts,
            scope=settings.UserSettings.SCOPE_PROJECT
        )

    def set_context(self, context):
        """
        Set the context to display in the widget.
        """
        logger.debug("Setting up %s for context %s" % (self, context))

        self._context = context
        self._show_context(context)

        # ensure the new context is added to the list of recents
        # TODO: only do this when publishing
        #self._add_to_recents(context)

    def set_up(self, task_manager):
        """
        Handles initial set up of the widget. Includes setting up menu, running
        any background set up tasks, etc.

        :param task_manager:
        :return:
        """

        # attach the context menu
        self.ui.task_menu_btn.setMenu(self._task_menu)
        self._task_menu.aboutToShow.connect(
            self._on_about_to_show_contexts_menu)

        # setup the search toggle
        self.ui.task_search_btn.toggled.connect(self._on_task_search_toggled)
        self.ui.task_search.hide()

        # setup the search toggle
        self.ui.link_search_btn.toggled.connect(self._on_link_search_toggled)
        self.ui.link_search.hide()

        # set up the task manager to the task search widget
        self.ui.task_search.set_placeholder_text("Search for Tasks...")
        self.ui.task_search.set_bg_task_manager(task_manager)
        self.ui.task_search.entity_activated.connect(
            self._on_entity_activated)

        # save as above but for the link search widget
        self.ui.link_search.set_placeholder_text("Search for entity link...")
        self.ui.link_search.set_bg_task_manager(task_manager)
        self.ui.link_search.entity_activated.connect(
            self._on_entity_activated
        )

        # set up event filters for the task/link display labels so that when
        # clicked, they go directly to an edit state
        self.ui.task_display.installEventFilter(self)
        self.ui.link_display.installEventFilter(self)

        # setup event filters for the task/link search inputs so that when
        # certain keys are pressed, the widget can react to it properly
        self.ui.task_search.installEventFilter(self)
        self.ui.link_search.installEventFilter(self)

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

        # Query Shotgun for valid entity types for PublishedFile.entity field
        self._schema_query_id = task_manager.add_task(
            _query_publishedfile_entity_schema)

        # query all my assigned tasks in a bg task
        self._my_tasks_query_id = task_manager.add_task(_query_my_tasks)

        # get recent contexts from user settings
        self._get_recent_contexts()

    def _add_to_recents(self, context):

        recent_actions = self._menu_actions["Recent"]

        matching_indexes = []
        for i, recent_action in enumerate(recent_actions):
            recent_context = recent_action.data()
            if recent_context == context:
                # contexts support __eq__ so this should be enough for comparing
                matching_indexes.append(i)

        if matching_indexes:
            # context exists in recent list in one or more places. remove the
            # QAction(s) and put one of them at the front of the list
            recent_action = None
            for match_index in matching_indexes:
                recent_action = recent_actions.pop(match_index)
        else:
            # the context does not exist in the recents. add it
            recent_action = self._get_qaction_for_context(context)

        if recent_action:
            recent_actions.insert(0, recent_action)

        # only keep the 5 most recent
        self._menu_actions["Recent"] = recent_actions[:5]

    def _build_my_tasks_actions(self, my_tasks):

        publisher = sgtk.platform.current_bundle()

        # ---- build my tasks section

        if my_tasks:

            task_actions = []

            for task in my_tasks:
                task_context = publisher.sgtk.context_from_entity(
                    task["type"], task["id"])
                task_action = self._get_qaction_for_context(task_context)

                task_actions.append(task_action)
                self._menu_actions["My Tasks"].append(task_action)
        else:
            logger.info("No tasks found for current user: %s" % (
                publisher.context.user,))

    def _get_qaction_for_context(self, context):

        context_display = _get_context_display(context, plain_text=True)
        icon_path = _get_context_icon_path(context)

        action = QtGui.QAction(self)
        action.setText(context_display)
        action.setIcon(QtGui.QIcon(icon_path))
        action.setData(context)
        action.triggered.connect(
            lambda c=context: self._on_context_activated(c))

        return action

    def _get_recent_contexts(self):

        serialized_recent_contexts = self._settings.retrieve(
            self._settings_recent_contexts_key,
            default=[],
            scope=settings.UserSettings.SCOPE_PROJECT
        )

        # turn these into QActions to add to the list of recents in the menu
        for serialized_context in serialized_recent_contexts:
            context = sgtk.Context.deserialize(serialized_context)
            recent_action = self._get_qaction_for_context(context)
            self._menu_actions["Recent"].append(recent_action)

    def _on_about_to_show_contexts_menu(self):

        # clear and rebuild the menu since the recents section is dynamic
        self._task_menu.clear()

        # ---- build the "Recent" menu

        recent_actions = self._menu_actions["Recent"]

        if recent_actions:
            self._task_menu.add_group(recent_actions, "Recent")

        # ---- build the "My Tasks" menu

        my_tasks_actions = self._menu_actions["My Tasks"]

        if my_tasks_actions:
            self._task_menu.add_group(my_tasks_actions, "My Tasks")

    def _on_context_activated(self, context):

        self._show_context(context)
        self.context_changed.emit(context)

    def _on_entity_activated(self, entity_type, entity_id, entity_name):

        publisher = sgtk.platform.current_bundle()
        context = publisher.sgtk.context_from_entity(entity_type, entity_id)
        self._on_context_activated(context)

    def _on_task_search_toggled(self, checked):

        if checked:
            self.ui.task_display.hide()
            self.ui.task_menu_btn.hide()
            self.ui.task_search.show()
            self.ui.task_search.setFocus()

            if self._context:
                entity = self._context.entity or self._context.project or None
                search_str = entity["name"]
                if self._context.task:
                    search_str = "%s %s " % (
                        search_str, self._context.task["name"])
                self.ui.task_search.setText(search_str)
                self.ui.task_search.completer().search(search_str)
                self.ui.task_search.completer().complete()
        else:
            self.ui.task_display.show()
            self.ui.task_menu_btn.show()
            self.ui.task_search.hide()

    def _on_link_search_toggled(self, checked):

        if checked:
            self.ui.link_display.hide()
            self.ui.link_search.show()
            self.ui.link_search.setFocus()

            if self._context:
                entity = self._context.entity or self._context.project or None
                search_str = entity["name"]
                self.ui.link_search.setText(search_str)
                self.ui.link_search.completer().search(search_str)
                self.ui.link_search.completer().complete()
        else:
            self.ui.link_display.show()
            self.ui.link_search.hide()

    def _on_task_completed(self, task_id, group, result):
        """
        Handle the results of our published file entity field schema query.
        """

        if task_id == self._schema_query_id:
            self._restrict_searchable_entity_types(result)

        elif task_id == self._my_tasks_query_id:
            self._build_my_tasks_actions(result)

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

    def _restrict_searchable_entity_types(self, published_file_entity_schema):

        # drill down into the schema to retrieve the valid types for the
        # field. this is ugly, but will ensure we get a list no matter what
        entity_types = published_file_entity_schema. \
            get("entity", {}). \
            get("properties", {}). \
            get("valid_types", {}). \
            get("value", [])

        # always include Project and Tasks
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

        # update the types for the link completer
        self.ui.link_search.set_searchable_entity_types(
            entity_types_dict)

        task_types_dict = copy.deepcopy(entity_types_dict)

        # the task search can complete anything, entities or tasks
        task_types_dict["Task"] = []

        # now update the types for the task completer
        self.ui.task_search.set_searchable_entity_types(task_types_dict)

    def _show_context(self, context):

        task_display = _get_task_display(context)
        link_display = _get_link_display(context)

        self.ui.task_display.setText(task_display)
        self.ui.task_search_btn.setChecked(False)
        self.ui.task_search_btn.setDown(False)

        self.ui.link_display.setText(link_display)
        self.ui.link_search_btn.setChecked(False)
        self.ui.link_search_btn.setDown(False)


def _get_task_display(context, plain_text=False):

    if not context.task:
        return ""

    task_name = context.task["name"]

    if plain_text:
        display_name = task_name
    else:
        task_type = context.task["type"]
        task_icon = "<img src='%s'>" % (
            shotgun_globals.get_entity_type_icon_url(task_type),)
        display_name = "%s&nbsp;%s" % (task_icon, task_name)

    return display_name


def _get_link_display(context, plain_text=False):

    entity = context.entity or context.project or None

    if not entity:
        return ""

    entity_name = entity["name"]

    if plain_text:
        display_name = entity_name
    else:
        entity_type = entity["type"]
        entity_icon = "<img src='%s'>" % (
            shotgun_globals.get_entity_type_icon_url(entity_type),)
        display_name = "%s&nbsp;%s" % (entity_icon, entity_name)

    return display_name


def _get_context_display(context, plain_text=False):

    task_display = _get_task_display(context, plain_text=plain_text)
    link_display = _get_link_display(context, plain_text=plain_text)

    display_name = link_display

    if task_display:

        if plain_text:
            display_name = "%s > %s" % (display_name, task_display)
        else:
            display_name = """
                %s&nbsp;&nbsp;<b><code>&gt;</code></b>&nbsp;&nbsp;%s
            """ % (link_display, task_display)

    return display_name


def _get_context_icon_path(context):

    if context.entity:
        entity_type = context.entity["type"]
        return shotgun_globals.get_entity_type_icon_url(entity_type)
    elif context.task:
        return shotgun_globals.get_entity_type_icon_url("Task")
    elif context.project:
        return shotgun_globals.get_entity_type_icon_url("Project")
    else:
        return ""


def _query_my_tasks():

    publisher = sgtk.platform.current_bundle()
    project = publisher.context.project
    current_user = publisher.context.user

    filters = [
        ["project", "is", project],
        ["task_assignees", "is", current_user],
        ["project.Project.sg_status", "is", "Active"]
    ]

    order = [
        {"field_name": "entity", "direction": "asc"},
        {"field_name": "content", "direction": "asc"}
    ]

    return publisher.shotgun.find(
        "Task",
        filters,
        fields=["id", "content", "entity"],
        order=order
    )


def _query_publishedfile_entity_schema():

    publisher = sgtk.platform.current_bundle()
    project = publisher.context.project

    return publisher.shotgun.schema_field_read(
        "PublishedFile",
        field_name="entity",
        project_entity=project
    )
