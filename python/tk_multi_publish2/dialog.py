# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import traceback

import sgtk
from sgtk.platform.qt import QtCore, QtGui

from .ui.dialog import Ui_Dialog
from .processing import PluginManager, Task, Item
from .progress import ProgressHandler
from .summary_overlay import SummaryOverlay
from .publish_tree_widget import TreeNodeItem, TopLevelTreeNodeItem

# import frameworks
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")
help_screen = sgtk.platform.import_framework("tk-framework-qtwidgets", "help_screen")
task_manager = sgtk.platform.import_framework("tk-framework-shotgunutils", "task_manager")
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")


logger = sgtk.platform.get_logger(__name__)


class AppDialog(QtGui.QWidget):
    """
    Main dialog window for the App
    """

    # main drag and drop areas
    (DRAG_SCREEN, PUBLISH_SCREEN) = range(2)

    # details ui panes
    (ITEM_DETAILS, TASK_DETAILS, PLEASE_SELECT_DETAILS, MULTI_EDIT_NOT_SUPPORTED) = range(4)

    def __init__(self, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        QtGui.QWidget.__init__(self, parent)

        # create a settings manager where we can pull and push prefs later
        # prefs in this manager are shared
        self._settings_manager = settings.UserSettings(sgtk.platform.current_bundle())

        # create a background task manager
        self._task_manager = task_manager.BackgroundTaskManager(
            self,
            start_processing=True,
            max_threads=2
        )

        # register the data fetcher with the global schema manager
        shotgun_globals.register_bg_task_manager(self._task_manager)

        self._bundle = sgtk.platform.current_bundle()
        self._validation_run = False

        # set up the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.context_widget.set_up(self._task_manager)
        self.ui.context_widget.restrict_entity_types_by_link("PublishedFile", "entity")

        self.ui.context_widget.set_task_tooltip(
            "<p>The task that the selected item will be associated with "
            "in Shotgun after publishing. It is recommended to always "
            "fill out the Task field when publishing. The menu button "
            "to the right will provide suggestions for Tasks to publish "
            "to including the Tasks assigned to you, recently used Tasks, "
            "and Tasks related to the entity Link populated in the field below.</p>"
        )
        self.ui.context_widget.set_link_tooltip(
            "<p>The entity that the selected item will be associated with "
            "in Shotgun after publishing. By selecting a Task in the field "
            "above, the Link will automatically be populated. It is recommended "
            "that you always populate the Task field when publishing. "
            "The Task menu above will display any tasks associated with "
            "the entity populated in this field.</p>"
        )

        self.ui.context_widget.context_changed.connect(self._on_item_context_change)

        # make sure the splitter expands the detail area only
        self.ui.splitter.setStretchFactor(0, 0)
        self.ui.splitter.setStretchFactor(1, 1)

        # give tree view 360 width, rest to details pane
        # note: value of second option does not seem to
        # matter (as long as it's there)
        self.ui.splitter.setSizes([360, 100])

        # drag and drop
        self.ui.frame.something_dropped.connect(self._on_drop)
        self.ui.large_drop_area.something_dropped.connect(self._on_drop)
        self.ui.items_tree.tree_reordered.connect(self._synchronize_tree)

        # hide the drag screen progress button by default
        self.ui.drag_progress_message.hide()

        # buttons
        self.ui.validate.clicked.connect(self.do_validate)
        self.ui.publish.clicked.connect(self.do_publish)
        self.ui.close.clicked.connect(self.close)
        self.ui.close.hide()

        # overlay
        self._overlay = SummaryOverlay(self.ui.main_frame)
        self._overlay.publish_again_clicked.connect(self._publish_again_clicked)

        # settings
        self.ui.items_tree.status_clicked.connect(self._on_publish_status_clicked)

        # when the description is updated
        self.ui.item_comments.textChanged.connect(self._on_item_comment_change)

        # selection in tree view
        self.ui.items_tree.itemSelectionChanged.connect(self._update_details_from_selection)

        # clicking in the tree view
        self.ui.items_tree.checked.connect(self._update_details_from_selection)

        # thumbnails
        self.ui.item_thumbnail.screen_grabbed.connect(self._update_item_thumbnail)

        # tool buttons
        self.ui.delete_items.clicked.connect(self._delete_selected)
        self.ui.expand_all.clicked.connect(lambda: self._set_tree_items_expanded(True))
        self.ui.collapse_all.clicked.connect(lambda: self._set_tree_items_expanded(False))
        self.ui.refresh.clicked.connect(self._full_rebuild)

        # stop processing logic
        # hide the stop processing button by default
        self.ui.stop_processing.hide()
        self._stop_processing_flagged = False
        self.ui.stop_processing.clicked.connect(self._trigger_stop_processing)

        # help button
        help_url = self._bundle.get_setting("help_url")
        if help_url:
            # connect the help button to the help url provided in the settings
            self.ui.help.clicked.connect(lambda: self._open_url(help_url))
        else:
            # no url. hide the button!
            self.ui.help.hide()

        # browse file action
        self._browse_file_action = QtGui.QAction(self)
        self._browse_file_action.setText("Browse files to publish")
        self._browse_file_action.setIcon(
            QtGui.QIcon(":/tk_multi_publish2/file.png"))
        self._browse_file_action.triggered.connect(
            lambda: self._on_browse(folders=False))

        # browse folder action
        self._browse_folder_action = QtGui.QAction(self)
        self._browse_folder_action.setText(
            "Browse folders to publish image sequences")
        self._browse_folder_action.setIcon(QtGui.QIcon(
            ":/tk_multi_publish2/image_sequence.png"))
        self._browse_folder_action.triggered.connect(
            lambda: self._on_browse(folders=True))

        # browse menu
        self._browse_menu = QtGui.QMenu(self)
        self._browse_menu.addAction(self._browse_file_action)
        self._browse_menu.addAction(self._browse_folder_action)

        # browse tool button
        self.ui.browse.clicked.connect(self._on_browse)
        self.ui.browse.setMenu(self._browse_menu)
        self.ui.browse.setPopupMode(QtGui.QToolButton.DelayedPopup)

        # drop area browse button. Note, not using the actions created above
        # because making the buttons look right when they're usingt he action's
        # text/icon proved difficult. Instead, the button text/icon are defined
        # in the designer file. So as a note, if you want to change the text or
        # icon, you'll need to do it above and in designer.
        self.ui.drop_area_browse_file.clicked.connect(
            lambda: self._on_browse(folders=False))
        self.ui.drop_area_browse_seq.clicked.connect(
            lambda: self._on_browse(folders=True))

        # currently displayed item
        self._current_item = None

        # Currently selected tasks. If a selection is created in the GUI that contains multiple
        # task types or even other tree item types, then, _current_tasks will be set to an empty
        # selection, regardless of the number of the items actually selected in the UI.
        self._current_tasks = _TaskSelection()

        # start up our plugin manager
        self._plugin_manager = None

        self._summary_comment = ""
        # this boolean indicates that at least one child has a description that is different than the summary.
        self._summary_comment_multiple_values = False

        # set up progress reporting
        self._progress_handler = ProgressHandler(
            self.ui.progress_status_icon,
            self.ui.progress_message,
            self.ui.progress_bar
        )

        # link the summary overlay status button with the log window
        self._overlay.info_clicked.connect(
            self._progress_handler._progress_details.toggle)

        # connect the drag screen progress button to show the progress details
        self.ui.drag_progress_message.clicked.connect(
            self._progress_handler.show_details)

        # hide settings for now
        self.ui.item_settings_label.hide()
        self.ui.item_settings.hide()

        # create a plugin manager
        self._plugin_manager = PluginManager(self._progress_handler.logger)
        self.ui.items_tree.set_plugin_manager(self._plugin_manager)

        # this is the pixmap in the summary thumbnail
        self._summary_thumbnail = None 

        # set publish button text
        self._display_action_name = self._bundle.get_setting("display_action_name")
        self.ui.publish.setText(self._display_action_name)

        # Special UI tweaks based on the 'manual_load_enabled' property
        #
        # Hide the tiny label at bottom of the tree view and
        # the browse button in the button container
        self.ui.text_below_item_tree.setVisible(self.manual_load_enabled)
        self.ui.browse.setVisible(self.manual_load_enabled)

        # run collections
        self._full_rebuild()

    @property
    def manual_load_enabled(self):
        """ Returns whether user is allowed to load file to the UI """
        return self._bundle.get_setting("enable_manual_load")

    def keyPressEvent(self, event):
        """
        Qt Keypress event
        """
        # if our log details ui is showing and escape
        # is pressed, capture it and hide the log details ui
        if self._progress_handler.is_showing_details() and \
                event.key() == QtCore.Qt.Key_Escape:
            # hide log window
            self._progress_handler.hide_details()

        else:
            super(AppDialog, self).keyPressEvent(event)

    def closeEvent(self, event):
        """
        Executed when the main dialog is closed.
        All worker threads and other things which need a proper shutdown
        need to be called here.
        """
        logger.debug("CloseEvent Received. Begin shutting down UI.")

        # register the data fetcher with the global schema manager
        shotgun_globals.unregister_bg_task_manager(self._task_manager)

        # deallocate loggers
        self._progress_handler.shut_down()

        try:
            # shut down main threadpool
            self._task_manager.shut_down()
        except Exception:
            logger.exception("Error running Shotgun Panel App closeEvent()")

        # ensure the context widget's recent contexts are saved
        self.ui.context_widget.save_recent_contexts()

    def _update_details_from_selection(self):
        """
        Makes sure that the right hand side details section reflects the selected item in the left
        hand side tree.
        """

        # look at how many items are checked
        checked_top_items = 0
        for context_index in xrange(self.ui.items_tree.topLevelItemCount()):
            context_item = self.ui.items_tree.topLevelItem(context_index)
            for child_index in xrange(context_item.childCount()):
                child_item = context_item.child(child_index)
                if child_item.enabled:
                    checked_top_items += 1

        if checked_top_items == 0:
            # disable buttons
            self.ui.publish.setEnabled(False)
            self.ui.validate.setEnabled(False)
        else:
            self.ui.publish.setEnabled(True)
            self.ui.validate.setEnabled(True)

        # now look at selection
        items = self.ui.items_tree.selectedItems()

        if self._is_task_selection_homogeneous(items):
            # We should update the tasks details ui.
            self._current_item = None
            publish_tasks = _TaskSelection([item.get_publish_instance() for item in items])
            self._update_task_details_ui(publish_tasks)
        elif len(items) != 1:
            # Otherwise we can't show items from a multi-selection, so inform the user.
            self._current_item = None
            self._update_task_details_ui()
            # show overlay with 'please select single item'
            self.ui.details_stack.setCurrentIndex(self.PLEASE_SELECT_DETAILS)
        else:
            # 1 item selected
            tree_item = items[0]
            publish_object = tree_item.get_publish_instance()
            if isinstance(publish_object, Item):
                self._update_task_details_ui()
                self._create_item_details(tree_item)
            elif publish_object is None:
                self._update_task_details_ui()
                # top node summary
                self._create_master_summary_details()

    def _is_task_selection_homogeneous(self, items):
        """
        Indicates if a selection is made up only of tasks and they are all of the same item.

        :param items: List of tree node items.

        :returns: ``True`` is the selection only contains tasks, ``False`` otherwise.
        """
        # If the list is empty, we don't have a task selection.
        if len(items) == 0:
            return False

        # Grab the first item in the list, which we will use to compare to every other item. If
        # all items end up being the same type as the first one, then we have a homogeneous list
        # of tasks.
        first_task = items[0].get_publish_instance()

        for item in items:

            publish_instance = item.get_publish_instance()
            # User has mixed different types of publish instances, it's not just a task list.
            if not isinstance(publish_instance, Task):
                return False

            # There's a task that's not of the same type as the others, we're done!
            if not first_task.is_same_task_type(publish_instance):
                return False

        return True

    def _update_task_details_ui(self, new_task_selection=None):
        """
        Updates the plugin UI widget.

        This method should be called if everything is of the same type OR if the selection is
        empty.

        :param new_task_selection: A :class:`TaskSelection` containing the current UI selection.
        """
        new_task_selection = new_task_selection or _TaskSelection()

        # Nothing changed, so do nothing.
        if self._current_tasks == new_task_selection:
            return

        # We're changing task, so we need to backup the current settings.
        if self._current_tasks:
            logger.debug("Saving settings...")
            self._pull_settings_from_ui(self._current_tasks)

        # If we're moving to a task that doesn't have a custom UI, clear everything.
        if not new_task_selection:
            # Note: At this point we don't really care if current task actually had a UI, we can
            # certainly tear down an empty widget.
            logger.debug("The ui is going to change, so clear the current one.")
            self.ui.task_settings.widget = None
            self._current_tasks = new_task_selection
            return

        # A task was picked, so make sure our page is in foreground.
        self.ui.details_stack.setCurrentIndex(self.TASK_DETAILS)

        # set the header for the task plugin
        self.ui.task_icon.setPixmap(new_task_selection.plugin.icon)
        self.ui.task_name.setText(new_task_selection.plugin.name)

        # Now figure out if we need to create/replace the widgets.
        if (
            # If we had a selection before
            self._current_tasks and
            # and it was of the same type as the new one.
            self._current_tasks.is_same_task_type(new_task_selection)
        ):
            logger.debug("Reusing custom ui from %s.", new_task_selection.plugin)
        else:
            logger.debug("Building a custom ui for %s.", new_task_selection.plugin)
            widget = new_task_selection.plugin.run_create_settings_widget(
                self.ui.task_settings_parent)
            self.ui.task_settings.widget = widget

        # Update the UI with the settings from the current plugin.
        if self._push_settings_into_ui(new_task_selection):
            # Alright, we're ready to deal with the new task.
            self._current_tasks = new_task_selection
        else:
            self._current_tasks = _TaskSelection()

    def _pull_settings_from_ui(self, selected_tasks):
        """
        Retrieves settings from the UI and updates the task's settings.

        :param selected_tasks: A :class:`TaskSelection` of tasks to update based
            on the values edited in the UI.
        """
        if selected_tasks.has_custom_ui:
            widget = self.ui.task_settings.widget
            settings = self._current_tasks.get_settings(widget)
        else:
            # TODO: Implement getting the settings from the generic UI, if we ever implement one.
            settings = {}

        # Update the values in all the tasks.
        for task in selected_tasks:
            # The settings returned by the UI are actual value, not Settings objects, so apply each
            # value returned on the appropriate settings object.
            for k, v in settings.iteritems():
                task.settings[k].value = v

    def _push_settings_into_ui(self, selected_tasks):
        """
        Takes the settings from this task and pushes its values into the UI.

        :param selected_tasks: A :class:`TaskSelection` of tasks to update based
            on the values edited in the UI.
        """
        # The run_get_ui_settings expects a dictionary of the actual values, not Setting objects, so
        # translate the dictionary.
        tasks_settings = []
        for task in selected_tasks:
            settings_dict = {}
            for k, v in task.settings.iteritems():
                settings_dict[k] = v.value
            tasks_settings.append(settings_dict)

        if selected_tasks.has_custom_ui:
            try:
                selected_tasks.set_settings(self.ui.task_settings.widget, tasks_settings)
            except NotImplementedError:
                self.ui.details_stack.setCurrentIndex(self.MULTI_EDIT_NOT_SUPPORTED)
                return False
        else:
            # TODO: Implement setting the settings into the generic UI.
            pass
        return True

    def _on_publish_status_clicked(self, task_or_item):
        """
        Triggered when someone clicks the status icon in the tree
        """
        # make sure the progress widget is shown
        self._progress_handler.select_last_message(task_or_item)

    def _on_item_comment_change(self):
        """
        Callback when someone types in the
        publish comments box in the overview details pane
        """
        comments = self.ui.item_comments.toPlainText()
        # if this is the summary description...
        if self._current_item is None:
            if self._summary_comment != comments:
                self._summary_comment = comments

                # this is the summary item - so update all top level items and their children!
                for top_level_item in self._plugin_manager.top_level_items:
                    top_level_item.description = self._summary_comment
                    top_level_item._propagate_description_to_children()

                # all tasks have same description now, so set <multiple values> indicator to false
                self._summary_comment_multiple_values = False

            self.ui.item_comments._show_placeholder = self._summary_comment_multiple_values

        # the "else" below means if this is a publish item
        else:
            self._current_item.description = comments
            
            # <multiple values> placeholder text should not appear for individual items
            self.ui.item_comments._show_placeholder = False

            # if at least one task has a comment that is different than the summary description, set 
            # <multiple values> indicator to true 
            if self._summary_comment != comments:
                self._summary_comment_multiple_values = True

    def _update_item_thumbnail(self, pixmap):
        """
        Update the currently selected item with the given
        thumbnail pixmap
        """
        if not self._current_item:
            # this is the summary item
            self._summary_thumbnail = pixmap
            if pixmap:
                # update all items with the summary thumbnail
                for top_level_item in self._plugin_manager.top_level_items:
                    top_level_item.thumbnail = self._summary_thumbnail
                    top_level_item.thumbnail_explicit = False
                    top_level_item._propagate_thumbnail_to_children()
        else: 
            self._current_item.thumbnail = pixmap
            # specify that the new thumbnail overrides the one inherited from summary
            self._current_item.thumbnail_explicit = True 


    def _create_item_details(self, tree_item):
        """
        Render details pane for a given item
        """
        item = tree_item.get_publish_instance()

        self._current_item = item
        self.ui.details_stack.setCurrentIndex(self.ITEM_DETAILS)
        self.ui.item_icon.setPixmap(item.icon)

        self.ui.item_name.setText(item.name)
        self.ui.item_type.setText(item.display_type)

        # check the state of screenshot
        if item.thumbnail_enabled:
            # display and make thumbnail editable
            self.ui.item_thumbnail_label.show()
            self.ui.item_thumbnail.show()
            self.ui.item_thumbnail.setEnabled(True)

        elif not item.thumbnail_enabled and item.thumbnail:
            # show thumbnail but disabled
            self.ui.item_thumbnail_label.show()
            self.ui.item_thumbnail.show()
            self.ui.item_thumbnail.setEnabled(False)

        else:
            # hide thumbnail
            self.ui.item_thumbnail_label.hide()
            self.ui.item_thumbnail.hide()

        self.ui.item_description_label.setText("Description")
        self.ui.item_comments.setPlainText(item.description)

        # if summary thumbnail is defined, item thumbnail should inherit it
        # unless item thumbnail was set after summary thumbnail
        if self._summary_thumbnail and not item.thumbnail_explicit:
            item.thumbnail = self._summary_thumbnail
        
        self.ui.item_thumbnail._set_multiple_values_indicator(False)
        self.ui.item_thumbnail.set_thumbnail(item.thumbnail)
        

        # Items with default thumbnails should still be able to have override thumbnails set by the user
        self.ui.item_thumbnail.setEnabled(True)

        if item.parent.is_root():
            self.ui.context_widget.show()

            if item.context_change_allowed:
                self.ui.context_widget.enable_editing(
                    True,
                    "<p>Task and Entity Link to apply to the selected item:</p>"
                )
            else:
                self.ui.context_widget.enable_editing(
                    False,
                    "<p>Context changing has been disabled for this item. "
                    "It will be associated with "
                    "<strong><a style='color:#C8C8C8; text-decoration:none' "
                    "href='%s'>%s</a></strong></p>" %
                    (item.context.shotgun_url, item.context)
                )

            # set the context
            self.ui.context_widget.set_context(item.context)
        else:
            self.ui.context_widget.hide()

        # create summary
        self.ui.item_summary_label.show()
        summary = tree_item.create_summary()
        # generate a summary

        if len(summary) == 0:
            summary_text = "No items to process."

        else:
            summary_text = "<p>The following items will be processed:</p>"
            summary_text += "".join(["<p>%s</p>" % line for line in summary])

        self.ui.item_summary.setText(summary_text)

        # skip settings for now
        ## render settings
        #self.ui.item_settings.set_static_data(
        #    [(p, item.properties[p]) for p in item.properties]
        #)

    def _create_master_summary_details(self):
        """
        Render the master summary representation
        """
        self._current_item = None
        self.ui.details_stack.setCurrentIndex(self.ITEM_DETAILS)

        display_name = self._bundle.get_setting("display_name")
        self.ui.item_name.setText("%s Summary"%display_name)
        self.ui.item_icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/icon_256.png"))

        self.ui.item_thumbnail_label.show()
        self.ui.item_thumbnail.show()

        thumbnail_is_multiple_values = False
        for top_level_item in self._plugin_manager.top_level_items:
           if top_level_item._get_thumbnail_explicit_recursive():
               thumbnail_is_multiple_values = True
               break
      
        self.ui.item_thumbnail._set_multiple_values_indicator(thumbnail_is_multiple_values)
        self.ui.item_thumbnail.set_thumbnail(self._summary_thumbnail)

        # setting enabled to true to be able to take a snapshot to define the thumbnail 
        self.ui.item_thumbnail.setEnabled(True)

        self.ui.item_description_label.setText("Description for all items")
        self.ui.item_comments.setPlainText(self._summary_comment)

        # the item_comments PublishDescriptionFocus won't display placeholder text if it is in focus
        # so clearing the focus from that widget in order to see the <multiple values> warning once 
        # the master summary details page is opened
        self.ui.item_comments.clearFocus()
        self.ui.item_comments._show_placeholder = self._summary_comment_multiple_values

        # for the summary, attempt to display the appropriate context in the
        # context widget. if all publish items have the same context, display
        # that one. if there are multiple, show none and update the label to
        # reflect it.

        # iterate over all the tree items to find currently used contexts
        current_contexts = {}
        for it in QtGui.QTreeWidgetItemIterator(self.ui.items_tree):
            item = it.value()
            publish_instance = item.get_publish_instance()
            if isinstance(publish_instance, Item):
                context = publish_instance.context
                context_key = str(context)
                current_contexts[context_key] = context

        if len(current_contexts) == 1:
            # only one context being used by current items. prepopulate it in
            # the summary view's context widget
            context_key = current_contexts.keys()[0]
            self.ui.context_widget.set_context(current_contexts[context_key])
            context_label_text = "Task and Entity Link to apply to all items:"
        else:
            self.ui.context_widget.set_context(
                None,
                task_display_override=" -- Multiple values -- ",
                link_display_override=" -- Multiple values -- ",
            )
            context_label_text = (
                "Currently publishing items to %s contexts. "
                "Override all items here:" % (len(current_contexts),)
            )

        self.ui.context_widget.show()
        self.ui.context_widget.enable_editing(True, context_label_text)

        # create summary for all items
        # no need to have a summary since the main label says summary
        self.ui.item_summary_label.hide()

        (num_items, summary) = self.ui.items_tree.get_full_summary()
        self.ui.item_summary.setText(summary)
        self.ui.item_type.setText("%d tasks to execute" % num_items)

    def _full_rebuild(self):
        """
        Full rebuild of the plugin state. Everything is recollected.
        """
        self._progress_handler.set_phase(self._progress_handler.PHASE_LOAD)
        self._progress_handler.push("Collecting information")

        num_items_created = self._plugin_manager.run_collectors()

        num_errors = self._progress_handler.pop()

        if num_errors == 0 and num_items_created == 1:
            self._progress_handler.logger.info("One item discovered by publisher.")
        elif num_errors == 0 and num_items_created > 1:
            self._progress_handler.logger.info("%d items discovered by publisher." % num_items_created)
        elif num_errors > 0:
            self._progress_handler.logger.error("Errors reported. See log for details.")

        # make sure the ui is up to date
        self._synchronize_tree()

        # select summary
        self.ui.items_tree.select_first_item()

        # reset the validation flag
        self._validation_run = False

    def _on_drop(self, files):
        """
        When someone drops stuff into the publish.
        """

        # Short circuiting method disabling actual action performed on dropping to the target.
        if not self.manual_load_enabled:
            self._progress_handler.logger.error("Drag & drop disabled.")
            return

        # add files and rebuild tree
        self._progress_handler.set_phase(self._progress_handler.PHASE_LOAD)
        self._progress_handler.push("Processing dropped files")

        # pyside gives us back unicode. Make sure we convert it to strings
        str_files = []
        for f in files:
            if isinstance(f, unicode):
                str_files.append(f.encode("utf-8"))
            else:
                str_files.append(f)

        try:
            self.ui.main_stack.setCurrentIndex(self.PUBLISH_SCREEN)

            # ensure the progress details are parented here in case we get
            # stuck here.
            self._progress_handler.progress_details.set_parent(
                self.ui.main_frame)

            self._overlay.show_loading()
            self.ui.button_container.hide()
            num_items_created = self._plugin_manager.add_external_files(str_files)
            num_errors = self._progress_handler.pop()

            if num_errors == 0 and num_items_created == 0:
                self._progress_handler.logger.info("Nothing was added.")
            elif num_errors == 0 and num_items_created == 1:
                self._progress_handler.logger.info("One item was added.")
            elif num_errors == 0 and num_items_created > 1:
                self._progress_handler.logger.info("%d items were added." % num_items_created)
            elif num_errors == 1:
                self._progress_handler.logger.error("An error was reported. Please see the log for details.")
            else:
                self._progress_handler.logger.error("%d errors reported. Please see the log for details." % num_errors)

            # rebuild the tree
            self._synchronize_tree()

        finally:
            self._overlay.hide()
            self.ui.button_container.show()

        if (len(self._plugin_manager.top_level_items) == 0 and
            self.ui.main_stack.currentIndex() == self.DRAG_SCREEN):
            # there are no top-level items and we're still on the drag screen.
            # something not good happened. show a button to open the progress
            # details with additional info.

            self.ui.drag_progress_message.setText(
                "Could not determine items to %s. "
                "Click for more info..." %
                (self._display_action_name,)
            )
            self.ui.drag_progress_message.show()
        else:
            # there are items and/or we're no longer on the drag screen
            self.ui.drag_progress_message.hide()

        # lastly, select the summary
        self.ui.items_tree.select_first_item()

    def _synchronize_tree(self):
        """
        Redraws the ui and rebuilds data based on
        the low level plugin representation
        """
        if len(self._plugin_manager.top_level_items) == 0:
            if not self.manual_load_enabled:
                # No items collected and 'enable_manual_load' application option
                # false, display that special error overlay.
                self._show_no_items_error()
            else:
                # nothing in list. show the full screen drag and drop ui
                self.ui.main_stack.setCurrentIndex(self.DRAG_SCREEN)

                # ensure the progress details widget is available for overlay on the
                # drop area
                self._progress_handler.progress_details.set_parent(
                    self.ui.large_drop_area)
        else:
            self.ui.main_stack.setCurrentIndex(self.PUBLISH_SCREEN)

            # ensure the progress details widget is available for overlay on the
            # main frame of the publish ui
            self._progress_handler.progress_details.set_parent(
                self.ui.main_frame)
            self.ui.items_tree.build_tree()

    def _set_tree_items_expanded(self, expanded):
        """
        Expand/Collapse all top-level publish items in the left side tree

        :param boole expanded: Expand if True, Collapse otherwise
        """

        for it in QtGui.QTreeWidgetItemIterator(self.ui.items_tree):
            item = it.value()
            if isinstance(item, TopLevelTreeNodeItem):
                item.setExpanded(expanded)

    def _delete_selected(self):
        """
        Delete all selected items. Prompt the user.
        """
        # check with the user

        num_items = len(self.ui.items_tree.selectedItems())

        if num_items == 0:
            return

        if num_items > 1:
            msg = "This will remove %d items from the list." % num_items
        else:
            msg = "Remove the item from the list?"

        res = QtGui.QMessageBox.question(
            self,
            "Remove items?",
            msg,
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)

        if res == QtGui.QMessageBox.Cancel:
            return

        processing_items = []

        # delete from the tree
        for tree_item in self.ui.items_tree.selectedItems():
            if isinstance(tree_item, TreeNodeItem):
                processing_items.append(tree_item.item)

        for item in processing_items:
            self._plugin_manager.remove_top_level_item(item)

        self._synchronize_tree()

        self.ui.items_tree.select_first_item()

    def _check_all(self, checked):
        """
        Check all boxes in the currently active tree
        """
        def _check_r(parent):
            for child_index in xrange(parent.childCount()):
                child = parent.child(child_index)
                child.checkbox.setChecked(checked)
                _check_r(child)

        parent = self.ui.items_tree.invisibleRootItem()

        _check_r(parent)

    # set all nodes to "ready to go"
    def _reset_tree_icon_r(self, parent):
        """
        Clear the current progress icon recursively
        for the given tree node
        """
        for child_index in xrange(parent.childCount()):
            child = parent.child(child_index)
            child.reset_progress()
            self._reset_tree_icon_r(child)

    def _prepare_tree(self, number_phases):
        """
        Prepares the tree for processing.

        Will reset the progress bar and set it's max
        value based on the number of nodes plus the
        specified number of phases.

        Will clear status icons in the tree.

        :param int number_phases: Number of passes to run
        """

        self._set_tree_items_expanded(True)

        parent = self.ui.items_tree.invisibleRootItem()

        self._reset_tree_icon_r(parent)

        # set all nodes to "ready to go"
        def _begin_process_r(parent):
            total_number_nodes = 0
            for child_index in xrange(parent.childCount()):
                child = parent.child(child_index)
                if child.enabled:
                    # child is ticked
                    total_number_nodes += 1
                total_number_nodes += _begin_process_r(child)
            return total_number_nodes

        total_number_nodes = _begin_process_r(parent)
        # reset progress bar
        self._progress_handler.reset_progress(total_number_nodes * number_phases)


    def do_validate(self, standalone=True):
        """
        Perform a full validation

        :param bool standalone: Indicates that the validation runs on its own,
            not part of a publish workflow.
        :returns: number of issues reported
        """

        # Make sure that settings from the current selection are retrieved from the UI and applied
        # back on the tasks.
        self._pull_settings_from_ui(self._current_tasks)

        if standalone:
            self._prepare_tree(number_phases=1)

        # inform the progress system of the current mode
        self._progress_handler.set_phase(self._progress_handler.PHASE_VALIDATE)
        self._progress_handler.push("Running validation pass")

        num_issues = 0
        self.ui.stop_processing.show()
        try:
            parent = self.ui.items_tree.invisibleRootItem()
            num_issues = self._visit_tree_r(parent, lambda child: child.validate(standalone), "Validating")
        finally:
            self._progress_handler.pop()
            if self._stop_processing_flagged:
                self._progress_handler.logger.info("Processing aborted by user.")
            elif num_issues > 0:
                self._progress_handler.logger.error("Validation Complete. %d issues reported." % num_issues)
            else:
                self._progress_handler.logger.info("Validation Complete. All checks passed.")

            if standalone:
                # reset process aborted flag
                self._stop_processing_flagged = False
                self.ui.stop_processing.hide()
                # reset the progress
                self._progress_handler.reset_progress()

        # remember that validation has completed at least once
        self._validation_run = True

        return num_issues

    def do_publish(self):
        """
        Perform a full publish
        """
        publish_failed = False

        # hide the action buttons during publish
        self.ui.button_container.hide()

        # Make sure that settings from the current selection are retrieved from the UI and applied
        # back on the tasks.
        self._prepare_tree(number_phases=3)

        try:
            # show cancel button
            self.ui.stop_processing.show()

            # is the app configured to execute the validation when publish
            # is triggered?
            if self._bundle.get_setting("validate_on_publish"):
                # do_validate returns the number of issues encountered
                if self.do_validate(standalone=False) > 0:
                    self._progress_handler.logger.error(
                        "Validation errors detected. "
                        "Not proceeding with publish."
                    )
                    self.ui.button_container.show()
                    return

            # validation not required on publish, it has already run though
            elif self._validation_run:
                self._progress_handler.logger.info(
                    "Skipping validation pass just before publish. "
                    "It was already run manually.")

            # validation not required on publish. no validation done yet
            else:
                # get user confirmation that they would like to continue
                button_clicked = QtGui.QMessageBox.question(
                    self,
                    "%s without Validation?" % (self._display_action_name,),
                    "You are attempting to %s without validation. Are you sure "
                    "you wish to continue?" % (self._display_action_name,),
                    buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel
                )
                if button_clicked == QtGui.QMessageBox.Cancel:
                    # user does not want ot continue.
                    self.ui.button_container.show()
                    return

                self._progress_handler.logger.info(
                    "User skipped validation step.")

            if self._stop_processing_flagged:
                # stop processing
                self.ui.button_container.show()
                return

            # inform the progress system of the current mode
            self._progress_handler.set_phase(self._progress_handler.PHASE_PUBLISH)
            self._progress_handler.push("Running publishing pass")

            # clear all icons
            parent = self.ui.items_tree.invisibleRootItem()
            self._reset_tree_icon_r(parent)

            try:
                self._visit_tree_r(parent, lambda child: child.publish(), "Publishing")
            except Exception, e:
                # ensure the full error shows up in the log file
                logger.error("Publish error stack:\n%s" % (traceback.format_exc(),))
                # and log to ui
                self._progress_handler.logger.error("Error while publishing. Aborting.")
                publish_failed = True
            finally:
                self._progress_handler.pop()

            if not publish_failed and not self._stop_processing_flagged:
                # proceed with finalizing phase

                # inform the progress system of the current mode
                self._progress_handler.set_phase(self._progress_handler.PHASE_FINALIZE)
                self._progress_handler.push("Running finalizing pass")

                try:
                    # note: Bugfix SG-4584: Re-acquire the parent pointer as we are iterating.
                    # If publishing is long running, it's seems the root item pointer for some
                    # reason gets GCed. By getting a fresh handle, we ensure that we won't run
                    # into issues where the python object exists but the underlying C++ object
                    # has been deleted.
                    parent = self.ui.items_tree.invisibleRootItem()
                    self._visit_tree_r(parent, lambda child: child.finalize(), "Finalizing")
                except Exception, e:
                    # ensure the full error shows up in the log file
                    logger.error("Finalize error stack:\n%s" % (traceback.format_exc(),))
                    # and log to ui
                    self._progress_handler.logger.error("Error while finalizing. Aborting.")
                    publish_failed = True
                finally:
                    self._progress_handler.pop()

            # if stop processing was flagged, don't show summary at end
            if self._stop_processing_flagged:
                self._progress_handler.logger.info("Processing aborted by user.")
                self.ui.button_container.show()
                return

        finally:
            # hide cancel button
            self.ui.stop_processing.hide()
            # reset abort state
            self._stop_processing_flagged = False
            # reset the progress
            self._progress_handler.reset_progress()

        # disable validate and publish buttons
        # show close button instead
        self.ui.validate.hide()
        self.ui.publish.hide()
        self.ui.close.show()

        if publish_failed:
            self._progress_handler.logger.error("Publish Failed! For details, click here.")
            self._overlay.show_fail()
        else:

            # Publish succeeded
            # Log the toolkit "Published" metric
            try:
                self._bundle.log_metric("Published")
            except:
                # ignore all errors. ex: using a core that doesn't support metrics
                pass

            self._progress_handler.logger.info("Publish Complete! For details, click here.")
            self._overlay.show_success()

    def _publish_again_clicked(self):
        """
        Slot that should be called when summary overlay close button is clicked.
        """
        # clear dropped files
        self._plugin_manager.clear_external_files()
        self._synchronize_tree()

        # show publish and validate buttons
        self.ui.validate.show()
        self.ui.publish.show()
        self.ui.close.hide()

        self.ui.button_container.show()

        # hide summary overlay
        self._overlay.hide()

        # select summary
        self.ui.items_tree.select_first_item()

        # reset the validation flag
        self._validation_run = False

    def _visit_tree_r(self, parent, action, action_name):
        """
        Recursive visitor helper function that descends the tree.
        Checks the stop processing flag and in case it is triggered,
        aborts the recursion
        """
        number_true_return_values = 0

        for child_index in xrange(parent.childCount()):

            if self._stop_processing_flagged:
                return number_true_return_values

            child = parent.child(child_index)
            if child.enabled:
                if action_name:
                    self._progress_handler.push(
                        "%s - %s" % (action_name, child),
                        child.icon,
                        child.get_publish_instance()
                    )
                try:
                    # process this node
                    status = action(child)  # eg. child.validate(), child.publish() etc.
                    if not status:
                        number_true_return_values += 1

                    # kick progress bar
                    self._progress_handler.increment_progress()

                    # now process all children
                    number_true_return_values += self._visit_tree_r(
                        child,
                        action,
                        action_name
                    )
                finally:
                    if action_name:
                        self._progress_handler.pop()
        return number_true_return_values

    def _on_item_context_change(self, context):
        """
        Fires when a new context is selected for the current item
        """

        # For each of the scenarios below, we ensure that the item being updated
        # allows context change. The widget should be disabled for the single
        # item case, but we check to be completely sure. For the summary case,
        # we show the widget but we don't want to update selected items that
        # are on context change lockdown.
        sync_required = False

        if self._current_item is None:
            # this is the summary item - so update all items!
            for top_level_item in self._plugin_manager.top_level_items:
                if top_level_item.context_change_allowed:
                    top_level_item.context = context
                    sync_required = True
        else:
            if self._current_item.context_change_allowed:
                self._current_item.context = context
                sync_required = True

        if sync_required:
            self._synchronize_tree()

    def _on_browse(self, folders=False):
        """Opens a file dialog to browse to files for publishing."""

        # Redundant with disabling UI controls but short circuiting this method
        # further ensure that a user won't be able to browse for any file even
        # if a minor UI bug allows a way to do it.
        if not self.manual_load_enabled:
            return

        # options for either browse type
        options = [
            QtGui.QFileDialog.DontResolveSymlinks,
            QtGui.QFileDialog.DontUseNativeDialog
        ]

        if folders:
            # browse folders specifics
            caption = "Browse folders to publish image sequences"
            file_mode = QtGui.QFileDialog.Directory
            options.append(QtGui.QFileDialog.ShowDirsOnly)
        else:
            # browse files specifics
            caption = "Browse files to publish"
            file_mode = QtGui.QFileDialog.ExistingFiles

        # create the dialog
        file_dialog = QtGui.QFileDialog(parent=self, caption=caption)
        file_dialog.setLabelText(QtGui.QFileDialog.Accept, "Select")
        file_dialog.setLabelText(QtGui.QFileDialog.Reject, "Cancel")
        file_dialog.setFileMode(file_mode)

        # set the appropriate options
        for option in options:
            file_dialog.setOption(option)

        # browse!
        if not file_dialog.exec_():
            return

        # process the browsed files/folders for publishing
        paths = file_dialog.selectedFiles()
        if paths:
            # simulate dropping the files into the dialog
            self._on_drop(paths)

    def _open_url(self, url):
        """Opens the supplied url in the appropriate browser."""

        try:
            logger.debug("Opening url: '%s'." % (url,))
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        except Exception, e:
            logger.error("Failed to open url: '%s'. Reason: %s" % (url, e))

    def _trigger_stop_processing(self):
        """
        Triggers a request to stop processing
        """
        logger.info("Processing aborted.")
        self._stop_processing_flagged = True

    def _show_no_items_error(self):
        """
        Re-organize the UI for presenting the overlay with a special error message
        when the 'enable_manual_load' application option is false and there is no
        items collected.
        """
        # Hide everything but the close button.
        self.ui.validate.hide()
        self.ui.publish.hide()
        self.ui.button_container.hide()
        self.ui.progress_bar.hide()
        self.ui.close.show()

        self._progress_handler.logger.error("Drag & drop disabled.")

        self.ui.main_stack.setCurrentIndex(self.PUBLISH_SCREEN)
        self._overlay.show_no_items_error()


class _TaskSelection(object):
    """
    Allows to manipulate a task selection as if it was a single object. It will hold a list of
    publish tasks from the tree items. It also removes the tedium of testing for an empty array
    and indexing [0] when doing comparisons.

    This class assumes that every task is of the same plugin type.

    :param items: List of task for in the selection. Defaults to an empty list.
    """
    def __init__(self, items=None):
        self._items = items or []

    def is_same_task_type(self, task_selection):
        """
        Checks if this task selection is of the same type as another task selection.

        :param task_selection: List of :class:`Task`.

        :returns: ``True`` is the plugins are the same, ``False`` otherwise. Note that
            two empty lists are considered to be of the same type.
        """
        if self._items and task_selection._items:
            # we know all the items in the list are of the same type, so we can
            # simply compare them using the first item of each list.
            return self._items[0].is_same_task_type(task_selection._items[0])
        elif not self._items and not task_selection._items:
            return True
        else:
            return False

    @property
    def has_custom_ui(self):
        """
        Checks if this selection has a custom UI.

        :returns: ``True`` if the selection uses a custom UI, ``False`` otherwise.
        """
        if self._items:
            return self._items[0].plugin.has_custom_ui
        else:
            return False

    @property
    def plugin(self):
        """
        Returns the plugin associated with this selection.

        :returns: The :class:`Plugin` instance or ``None``.
        """
        if self._items:
            return self._items[0].plugin
        else:
            return None

    def get_settings(self, widget):
        """
        Retrieves the settings from the selection's custom UI.

        :param widget: Custom UI's widget.

        :returns: Dictionary of settings as regular Python literals.
        """
        if self._items:
            return self._items[0].plugin.run_get_ui_settings(widget)
        else:
            return {}

    def set_settings(self, widget, settings):
        """
        Sets the settings from the selection into the custom UI.

        :param widget: Custom UI's widget.
        :param settings: List of settings for all tasks.
        """
        if self._items:
            self._items[0].plugin.run_set_ui_settings(widget, settings)

    def __iter__(self):
        """
        Allows to iterate over items in the selection.
        """
        return iter(self._items)

    def __eq__(self, other):
        """
        Tests two selections for equality.
        """
        return self._items == other._items

    def __nonzero__(self):
        """
        :returns: ``True`` is the selection is not empty, ``False`` otherwise.
        """
        return bool(self._items)
