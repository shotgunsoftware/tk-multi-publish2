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

shotgun_menus = sgtk.platform.import_framework(
    "tk-framework-qtwidgets", "shotgun_menus")

shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals")

settings = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "settings")

from .ui.context_editor_widget import Ui_ContextWidget

logger = sgtk.platform.get_logger(__name__)


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

        # get an instance of user settings to save/restore values across
        # sessions
        self._settings = settings.UserSettings(self._bundle)
        self._settings_recent_contexts_key = "%s_recent_contexts" % (
            self._bundle,)

        # we will do a bg query that requires an id to catch results
        self._schema_query_id = None

        # another query to get all tasks assigned to the current user
        self._my_tasks_query_id = None

        # keep a handle on the current context
        self._context = None

        # menu for recent and user contexts
        self._context_menu = shotgun_menus.ShotgunMenu(self)
        self._context_menu.setObjectName("context_menu")
        self._context_menu.addAction("Loading...")

        # keep a handle on all actions created
        self._menu_actions = {
            "My Tasks": [],
            "Recent": []
        }

        # set up the UI
        self.ui = Ui_ContextWidget()
        self.ui.setupUi(self)

    def closeEvent(self, event):
        """
        Prior to close, save the recents list of contexts to disk via user
        settings.
        """

        # build a list of serialized recent contexts
        serialized_contexts = []
        for recent_action in self._menu_actions["Recent"]:
            recent_context = recent_action.data()
            serialized_contexts.append(recent_context.serialize())

        # store the recent contexts on disk. the scope is per-project
        settings.store(
            self._settings_recent_contexts_key,
            serialized_contexts,
            scope=settings.UserSettings.SCOPE_PROJECT
        )

    def set_up(self, task_manager):
        """
        Handles initial set up of the widget. Includes setting up menu, running
        any background set up tasks, etc.

        :param task_manager:
        :return:
        """

        # attach the context menu
        self.ui.context_menu_btn.setMenu(self._context_menu)
        self._context_menu.aboutToShow.connect(
            self._on_about_to_show_contexts_menu)

        # setup the search toggle
        self.ui.context_search_btn.toggled.connect(self._on_search_toggled)
        self.ui.context_search.hide()

        # first, set up the task manager to the search widget
        self.ui.context_search.set_placeholder_text("Search...")
        self.ui.context_search.set_bg_task_manager(task_manager)
        self.ui.context_search.entity_activated.connect(
            self._on_entity_activated)

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
            self._query_publishedfile_entity_schema)

        # query all my assigned tasks in a bg task
        self._my_tasks_query_id = task_manager.add_task(self._query_my_tasks)

        # get recent contexts from user settings
        self._get_recent_contexts()

    def _query_publishedfile_entity_schema(self):

        publisher = sgtk.platform.current_bundle()
        project = publisher.context.project

        return publisher.shotgun.schema_field_read(
            "PublishedFile",
            field_name="entity",
            project_entity=project
        )

    def _query_my_tasks(self):

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

    def _get_recent_contexts(self):

        serialized_recent_contexts = self._settings.retrieve(
            self._settings_recent_contexts_key,
            default=[],
            scope=settings.UserSettings.SCOPE_PROJECT
        )

        # turn these into QActions to add to the list of recents in the menu
        for serialized_context in serialized_recent_contexts:
            context = serialized_context.deserialize()
            recent_action = self._get_qaction_for_context(context)
            self._menu_actions["Recent"].append(recent_action)

    def _on_search_toggled(self, checked):

        if checked:
            self.ui.context_label.hide()
            self.ui.context_search.show()
            self.ui.context_search.setFocus()

            if self._context:
                entity = self._context.entity or self._context.project or None
                search_str = entity["name"]
                if self._context.task:
                    search_str = "%s %s " % (
                        search_str, self._context.task["name"])
                self.ui.context_search.setText(search_str)
                self.ui.context_search.completer().search(search_str)
                self.ui.context_search.completer().complete()
        else:
            self.ui.context_label.show()
            self.ui.context_search.hide()

    def _on_task_completed(self, task_id, group, result):
        """
        Handle the results of our published file entity field schema query.
        """

        if task_id == self._schema_query_id:
            self._restrict_searchable_entity_types(result)

        elif task_id == self._my_tasks_query_id:
            self._build_my_tasks_actions(result)

    def _restrict_searchable_entity_types(self, published_file_entity_schema):

        # drill down into the schema to retrieve the valid types for the
        # field. this is ugly, but will ensure we get a list no matter what
        entity_types = published_file_entity_schema. \
            get("entity", {}). \
            get("properties", {}). \
            get("valid_types", {}). \
            get("value", [])

        # always include Project and Tasks
        entity_types.extend(["Project", "Task"])

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
        self.ui.context_search.set_searchable_entity_types(
            entity_types_dict)

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

    def _on_about_to_show_contexts_menu(self):

        # clear and rebuild the menu since the recents section is dynamic
        self._context_menu.clear()

        # ---- build the "Recent" menu

        recent_actions = self._menu_actions["Recent"]

        if recent_actions:
            self._context_menu.add_group(recent_actions, "Recent")

        # ---- build the "My Tasks" menu

        my_tasks_actions = self._menu_actions["My Tasks"]

        if my_tasks_actions:

            more_my_tasks_menu = None
            if len(my_tasks_actions) > 5:
                more_my_tasks_menu = shotgun_menus.ShotgunMenu(self)
                more_my_tasks_menu.setTitle("More")
                more_my_tasks_menu.add_group(my_tasks_actions[5:], "My Tasks")

            top_my_tasks_actions = my_tasks_actions[:5]
            if more_my_tasks_menu:
                top_my_tasks_actions.append(more_my_tasks_menu)

            self._context_menu.add_group(top_my_tasks_actions, "My Tasks")

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

    def set_context(self, context):
        """
        Register a context with the widget
        """
        logger.debug("Setting up %s for context %s" % (self, context))

        self._context = context
        self._show_context(context)

        # ensure the new context is added to the list of recents
        self._add_to_recents(context)

    def _show_context(self, context):

        context_display = _get_context_display(context)
        context_url = self._get_context_url(context)

        color = sgtk.platform.constants.SG_STYLESHEET_CONSTANTS.get(
            "SG_LINK_COLOR",
            sgtk.platform.constants.SG_STYLESHEET_CONSTANTS[
                "SG_FOREGROUND_COLOR"]
        )

        hyperlink = """
            <span>
              <a href='%s' style='text-decoration: none; color: %s'>%s</a>
            </span>
        """ % (context_url, color, context_display)

        self.ui.context_label.setText(hyperlink)
        self.ui.context_search_btn.setChecked(False)
        self.ui.context_search_btn.setDown(False)

    def _on_entity_activated(self, entity_type, entity_id, entity_name):

        publisher = sgtk.platform.current_bundle()
        context = publisher.sgtk.context_from_entity(entity_type, entity_id)
        self._on_context_activated(context)

    def _on_context_activated(self, context):

        self._show_context(context)
        self.context_changed.emit(context)

    def _get_context_url(self, context):

        entity = context.entity or context.project or None

        if self._bundle.sgtk.shotgun_url.endswith("/"):
            url_base = self._bundle.sgtk.shotgun_url
        else:
            url_base = "%s/" % self._bundle.sgtk.shotgun_url

        if not entity:
            return url_base

        url_entity_id = entity["id"]
        url_entity_type = entity["type"]

        if context.task:
            url_entity_type = context.task["type"]
            url_entity_id = context.task["id"]

        return "%sdetail/%s/%d" % (url_base, url_entity_type, url_entity_id)


def _get_context_display(context, plain_text=False):

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

    if context.task:

        task_name = context.task["name"]

        if plain_text:
            display_name = "%s > %s" % (display_name, task_name)

        else:
            task_type = context.task["type"]
            task_icon = "<img src='%s'>" % (
                shotgun_globals.get_entity_type_icon_url(task_type),)

            display_name = """
                %s&nbsp;&nbsp;<b><code>&gt;</code></b>&nbsp;&nbsp;%s&nbsp;%s
            """ % (display_name, task_icon, task_name)

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

    return icon


