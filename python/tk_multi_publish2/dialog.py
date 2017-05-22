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
from sgtk import TankError
from sgtk.platform.qt import QtCore, QtGui

from .ui.dialog import Ui_Dialog
from .processing import PluginManager, Task, Item
from .progress import ProgressHandler
from .summary_overlay import SummaryOverlay


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
    (ITEM_DETAILS, TASK_DETAILS, PLEASE_SELECT_DETAILS) = range(3)

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

        # set up the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.context_widget.set_up(self._task_manager)
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

        # buttons
        self.ui.validate.clicked.connect(self.do_validate)
        self.ui.publish.clicked.connect(self.do_publish)
        self.ui.close.clicked.connect(self.close)
        self.ui.close.hide()

        # overlay
        self._overlay = SummaryOverlay(self.ui.main_frame)

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
        self.ui.expand_all.clicked.connect(self.ui.items_tree.expandAll)
        self.ui.collapse_all.clicked.connect(self._collapse_tree)
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

        # browse tool button
        self.ui.browse.clicked.connect(self._on_browse)

        # drop area browse button
        self.ui.drop_area_browse.clicked.connect(self._on_browse)

        # currently displayed item
        self._current_item = None

        # start up our plugin manager
        self._plugin_manager = None

        # set up progress reporting
        self._progress_handler = ProgressHandler(
            self.ui.progress_status_icon,
            self.ui.progress_message,
            self.ui.progress_bar
        )

        # hide settings for now
        self.ui.item_settings_label.hide()
        self.ui.task_settings_label.hide()
        self.ui.item_settings.hide()
        self.ui.task_settings.hide()

        # create a plugin manager
        self._plugin_manager = PluginManager(self._progress_handler.logger)
        self.ui.items_tree.set_plugin_manager(self._plugin_manager)

        # run collections
        self._full_rebuild()

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
        except Exception, e:
            logger.exception("Error running Shotgun Panel App closeEvent()")

    def _update_details_from_selection(self):
        """
        Makes sure that the right hand side
        details section reflects the selected item
        in the left hand side tree.
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

        if len(items) != 1:
            # show overlay with 'please select single item'
            self.ui.details_stack.setCurrentIndex(self.PLEASE_SELECT_DETAILS)

        else:
            # 1 item selected
            tree_item = items[0]

            publish_object = tree_item.get_publish_instance()
            if isinstance(publish_object, Task):
                self._create_task_details(publish_object)
            elif isinstance(publish_object, Item):
                self._create_item_details(tree_item)
            elif publish_object is None:
                # top node summary
                self._create_master_summary_details()

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
        if self._current_item is None:
            # this is the summary item - so update all items!
            for top_level_item in self._plugin_manager.top_level_items:
                top_level_item.description = comments
        else:
            self._current_item.description = comments

    def _update_item_thumbnail(self, pixmap):
        """
        Update the currently selected item with the given
        thumbnail pixmap
        """
        if not self._current_item:
            raise TankError("No current item set!")
        self._current_item.thumbnail = pixmap

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
        self.ui.item_thumbnail.set_thumbnail(item.thumbnail)

        if item.parent.is_root():
            self.ui.link_label.show()
            self.ui.context_widget.show()
            self.ui.context_widget.set_context(item.context)
        else:
            self.ui.link_label.hide()
            self.ui.context_widget.hide()

        # create summary
        self.ui.item_summary_label.show()
        summary = tree_item.create_summary()
        # generate a summary

        if len(summary) == 0:
            summary_text = "Nothing will published."

        else:
            summary_text = "<p>The following items will be published:</p>"
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

        self.ui.item_name.setText("Publish Summary")
        self.ui.item_icon.setPixmap(QtGui.QPixmap(":/tk_multi_publish2/icon_256.png"))

        self.ui.item_thumbnail_label.hide()
        self.ui.item_thumbnail.hide()

        self.ui.item_description_label.setText("Description to apply to all items")
        self.ui.item_comments.setPlainText("")

        # set context
        self.ui.link_label.hide()
        self.ui.context_widget.hide()

        # create summary for all items
        # no need to have a summary since the main label says summary
        self.ui.item_summary_label.hide()

        (num_items, summary) = self.ui.items_tree.get_full_summary()
        self.ui.item_summary.setText(summary)
        self.ui.item_type.setText("Publishing %d items" % num_items)

    def _create_task_details(self, task):
        """
        Render details pane for a given task
        """
        self._current_item = None
        self.ui.details_stack.setCurrentIndex(self.TASK_DETAILS)

        self.ui.task_icon.setPixmap(task.plugin.icon)
        self.ui.task_name.setText(task.plugin.name)

        self.ui.task_description.setText(task.plugin.description)

        # skip settings for now
        #self.ui.task_settings.set_data(task.settings.values())

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

    def _on_drop(self, files):
        """
        When someone drops stuff into the publish.
        """
        # add files and rebuild tree
        self._progress_handler.set_phase(self._progress_handler.PHASE_LOAD)
        self._progress_handler.push("Processing dropped files")

        try:
            self.ui.main_stack.setCurrentIndex(self.PUBLISH_SCREEN)
            self._overlay.show_loading()
            num_items_created = self._plugin_manager.add_external_files(files)
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

        # lastly, select the summary
        self.ui.items_tree.select_first_item()

    def _synchronize_tree(self):
        """
        Redraws the ui and rebuilds data based on
        the low level plugin representation
        """
        if len(self._plugin_manager.top_level_items) == 0:
            # nothing in list. show the full screen drag and drop ui
            self.ui.main_stack.setCurrentIndex(self.DRAG_SCREEN)
        else:
            self.ui.main_stack.setCurrentIndex(self.PUBLISH_SCREEN)
            self.ui.items_tree.build_tree()

    def _collapse_tree(self):
        """
        Contract all the nodes in the currently active left hand side tree
        """
        for context_index in xrange(self.ui.items_tree.topLevelItemCount()):
            context_item = self.ui.items_tree.topLevelItem(context_index)
            for child_index in xrange(context_item.childCount()):
                child_item = context_item.child(child_index)
                self.ui.items_tree.collapseItem(child_item)

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
            processing_items.append(tree_item.item)

        for item in processing_items:
            self._plugin_manager.remove_top_level_item(item)

        self._synchronize_tree()

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
        self.ui.items_tree.expandAll()

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
        if standalone:
            self._prepare_tree(number_phases=1)

        # inform the progress system of the current mode
        self._progress_handler.set_phase(self._progress_handler.PHASE_VALIDATE)
        self._progress_handler.push("Running validation pass")

        parent = self.ui.items_tree.invisibleRootItem()
        num_issues = 0
        self.ui.stop_processing.show()
        try:
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

        return num_issues

    def do_publish(self):
        """
        Perform a full publish
        """
        publish_failed = False

        self._prepare_tree(number_phases=3)

        try:
            # show cancel button
            self.ui.stop_processing.show()

            issues = self.do_validate(standalone=False)

            if issues > 0:
                self._progress_handler.logger.error("Validation errors detected. Not proceeding with publish.")
                return

            if self._stop_processing_flagged:
                # stop processing
                return

            # inform the progress system of the current mode
            self._progress_handler.set_phase(self._progress_handler.PHASE_PUBLISH)
            self._progress_handler.push("Running publishing pass")

            parent = self.ui.items_tree.invisibleRootItem()

            # clear all icons
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
            self._progress_handler.logger.info("Publish Complete! For details, click here.")
            self._overlay.show_success()

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

        if self._current_item is None:
            # this is the summary item - so update all items!
            for top_level_item in self._plugin_manager.top_level_items:
                top_level_item.context = context
        else:
            self._current_item.context = context

        self._synchronize_tree()

    def _on_browse(self):
        """Opens a file dialog to browse to files for publishing."""

        file_dialog = QtGui.QFileDialog(
            parent=self,
            caption="Browse files to publish"
        )
        file_dialog.setLabelText(QtGui.QFileDialog.Accept, "Select")
        file_dialog.setLabelText(QtGui.QFileDialog.Reject, "Cancel")
        file_dialog.setOption(QtGui.QFileDialog.DontResolveSymlinks)
        file_dialog.setOption(QtGui.QFileDialog.DontUseNativeDialog)
        file_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        if not file_dialog.exec_():
            return

        files = file_dialog.selectedFiles()
        if files:
            # simulate dropping the files into the dialog
            self._on_drop(files)

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