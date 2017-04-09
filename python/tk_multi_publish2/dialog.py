# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


import sgtk
from sgtk import TankError
from sgtk.platform.qt import QtCore, QtGui

from .ui.dialog import Ui_Dialog
from .processing import PluginManager

# import frameworks
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")
help_screen = sgtk.platform.import_framework("tk-framework-qtwidgets", "help_screen")
task_manager = sgtk.platform.import_framework("tk-framework-shotgunutils", "task_manager")

logger = sgtk.platform.get_logger(__name__)


class AppDialog(QtGui.QWidget):
    """
    Main dialog window for the App
    """

    # main drag and drop areas
    (DRAG_SCREEN, PUBLISH_SCREEN) = range(2)

    # details ui panes
    (ITEM_DETAILS, TASK_DETAILS) = range(2)

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

        self._bundle = sgtk.platform.current_bundle()

        # set up the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

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

        # buttons
        self.ui.validate.clicked.connect(self.do_validate)
        self.ui.publish.clicked.connect(self._on_publish_click)
        self._close_ui_on_publish_click = False

        # settings
        self.ui.items_tree.settings_clicked.connect(self._create_task_details)
        self.ui.items_tree.status_clicked.connect(self._on_publish_status_clicked)

        # create menu on the cog button
        self._menu = QtGui.QMenu()
        self._actions = []
        self.ui.options.setMenu(self._menu)

        self._refresh_action = QtGui.QAction("Refresh", self)
        self._refresh_action.setIcon(QtGui.QIcon(QtGui.QPixmap(":/tk_multi_publish2/reload.png")))
        self._refresh_action.triggered.connect(self._refresh)
        self._menu.addAction(self._refresh_action)

        self._separator_1 = QtGui.QAction(self)
        self._separator_1.setSeparator(True)
        self._menu.addAction(self._separator_1)

        self._expand_action = QtGui.QAction("Expand All", self)
        self._expand_action.triggered.connect(self._expand_tree)
        self._menu.addAction(self._expand_action)

        self._collapse_action = QtGui.QAction("Collapse All", self)
        self._collapse_action.triggered.connect(self._collapse_tree)
        self._menu.addAction(self._collapse_action)

        self._separator_2 = QtGui.QAction(self)
        self._separator_2.setSeparator(True)
        self._menu.addAction(self._separator_2)

        self._check_all_action = QtGui.QAction("Check All", self)
        self._check_all_action.triggered.connect(lambda: self._check_all(True))
        self._menu.addAction(self._check_all_action)

        self._uncheck_all_action = QtGui.QAction("Uncheck All", self)
        self._uncheck_all_action.triggered.connect(lambda: self._check_all(False))
        self._menu.addAction(self._uncheck_all_action)

        # when the description is updated
        self.ui.item_comments.textChanged.connect(self._on_item_comment_change)

        # selection in tree view
        self.ui.items_tree.itemSelectionChanged.connect(self._update_details_from_selection)

        # thumbnails
        self.ui.item_thumbnail.screen_grabbed.connect(self._update_item_thumbnail)

        # currently displayed item
        self._current_item = None

        # start up our plugin manager
        self._plugin_manager = None

        # start it up
        self._refresh()

    def closeEvent(self, event):
        """
        Executed when the main dialog is closed.
        All worker threads and other things which need a proper shutdown
        need to be called here.
        """
        logger.debug("CloseEvent Received. Begin shutting down UI.")

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
        items = self.ui.items_tree.selectedItems()

        # TODO ---- FIX THIS

        # if len(items) == 0:
        #     tree_item = None
        # else:
        #     tree_item = items[0]
        #
        # # make sure we are focused on the details tab
        # self.ui.right_tabs.setCurrentIndex(self.DETAILS_TAB)
        #
        # if tree_item is None:
        #     self.ui.details_stack.setCurrentIndex(self.BLANK_DETAILS)
        #
        # elif tree_item.parent() is None and isinstance(tree_item, PublishTreeWidgetItem):
        #     # top level item
        #     self._create_summary_details(tree_item.item)
        #
        # elif isinstance(tree_item, PublishTreeWidgetItem):
        #     self._create_item_details(tree_item.item)
        #
        # elif isinstance(tree_item, PublishTreeWidgetTask):
        #     self._create_task_details(tree_item.task)
        #
        # elif isinstance(tree_item, PublishTreeWidgetPlugin):
        #     self._create_plugin_details(tree_item.plugin)
        #
        # else:
        #     raise TankError("Unknown selection")

    def _on_publish_status_clicked(self, task_or_item):
        """
        Triggered when someone clicks the status icon in the tree
        """
        # make sure the progress widget is shown
        self.ui.progress_widget.show()
        # select item
        self.ui.progress_widget.select_last_message(task_or_item)

    def _on_item_comment_change(self):
        """
        Callback when someone types in the
        publish comments box in the overview details pane
        """
        comments = self.ui.summary_comments.toPlainText()
        if not self._current_item:
            raise TankError("No current item set!")
        self._current_item.description = comments

    def _update_item_thumbnail(self, pixmap):
        """
        Update the currently selected item with the given
        thumbnail pixmap
        """
        if not self._current_item:
            raise TankError("No current item set!")
        self._current_item.thumbnail = pixmap

    def _create_item_details(self, item):

        self._current_item = item
        self.ui.details_stack.setCurrentIndex(self.ITEM_DETAILS)
        self.ui.item_icon.setPixmap(item.icon)

        self.ui.item_name.setText(item.name)
        self.ui.item_type.setText(item.display_type)

        self.ui.item_comments.setPlainText(item.description)
        self.ui.item_thumbnail.set_thumbnail(item.thumbnail)
        self.ui.item_context.setText(str(item.context))

        self.ui.item_settings.set_static_data(
            [(p, item.properties[p]) for p in item.properties]
        )

    def _create_task_details(self, task):

        self._current_item = None
        self.ui.details_stack.setCurrentIndex(self.TASK_DETAILS)

        self.ui.task_icon.setPixmap(task.plugin.icon)
        self.ui.task_name.setText(task.plugin.name)

        self.ui.task_description.setText(task.plugin.description)

        self.ui.task_settings.set_data(task.settings.values())


    def _refresh(self):

        self.ui.progress_widget.hide()

        self._reload_plugin_scan()

        if len(self._plugin_manager.top_level_items) == 0:
            # nothing in list. show the full screen drag and drop ui
            self.ui.main_stack.setCurrentIndex(self.DRAG_SCREEN)
        else:
            self.ui.main_stack.setCurrentIndex(self.PUBLISH_SCREEN)
            self.ui.items_tree.build_tree()
            self._select_top_items()

    def _select_top_items(self):

        # select the top item
        if self.ui.items_tree.topLevelItemCount() > 0:
            self.ui.items_tree.setCurrentItem(
                self.ui.items_tree.topLevelItem(0)
            )

    def _collapse_tree(self):
        """
        Contract all the nodes in the currently active left hand side tree
        """
        for item_index in xrange(self.ui.items_tree.topLevelItemCount()):
            item = self.ui.items_tree.topLevelItem(item_index)
            self.ui.items_tree.collapseItem(item)

    def _expand_tree(self):
        """
        Expand all the nodes in the currently active left hand side tree
        """
        for item_index in xrange(self.ui.items_tree.topLevelItemCount()):
            item = self.ui.items_tree.topLevelItem(item_index)
            self.ui.items_tree.expandItem(item)

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

    def _reload_plugin_scan(self):
        """

        """
        # run the hooks

        self._plugin_manager = PluginManager(self.ui.progress_widget.logger)
        self.ui.items_tree.set_plugin_manager(self._plugin_manager)


    def _prepare_tree(self, number_phases):

        self.ui.progress_widget.show()

        self._expand_tree()


        parent = self.ui.items_tree.invisibleRootItem()

        # set all nodes to "ready to go"
        def _begin_process_r(parent):
            total_number_nodes = 0
            for child_index in xrange(parent.childCount()):
                child = parent.child(child_index)
                child.reset_progress()
                if child.enabled:
                    # child is ticked
                    total_number_nodes += 1
                total_number_nodes += _begin_process_r(child)
            return total_number_nodes

        total_number_nodes = _begin_process_r(parent)
        # reset progress bar
        self.ui.progress_widget.reset_progress(total_number_nodes * number_phases)


    def do_validate(self, standalone=True):
        """
        Perform a full validation

        :returns: number of issues reported
        """
        if standalone:
            self._prepare_tree(number_phases=1)

        # inform the progress system of the current mode
        self.ui.progress_widget.set_phase(self.ui.progress_widget.PHASE_VALIDATE)
        self.ui.progress_widget.push("Running Validation pass")

        parent = self.ui.items_tree.invisibleRootItem()
        num_issues = 0
        try:
            num_issues = self._visit_tree_r(parent, lambda child: child.validate(standalone), "Validating")
        finally:
            self.ui.progress_widget.pop()
            if num_issues > 0:
                self.ui.progress_widget.logger.warning("Validation Complete. %d issues reported." % num_issues)
            else:
                self.ui.progress_widget.logger.info("Validation Complete. All checks passed.")

        return num_issues

    def _on_publish_click(self):
        """
        User clicked the publish/close button
        """
        if self._close_ui_on_publish_click:
            #
            self.close()
        else:
            self.do_publish()

    def do_publish(self):
        """
        Perform a full publish
        """
        self._prepare_tree(number_phases=3)

        issues = self.do_validate(standalone=False)

        if issues > 0:
            self.ui.progress_widget.logger.error("Validation errors detected. No proceeding with publish.")
            return

        # inform the progress system of the current mode
        self.ui.progress_widget.set_phase(self.ui.progress_widget.PHASE_PUBLISH)
        self.ui.progress_widget.push("Running publishing pass")

        parent = self.ui.items_tree.invisibleRootItem()
        try:
            self._visit_tree_r(parent, lambda child: child.publish(), "Publishing")
        except Exception, e:
            # todo - design a retry setup?
            self.ui.progress_widget.logger.error("Error while publishing. Aborting.")
            return
        finally:
            self.ui.progress_widget.pop()

        # inform the progress system of the current mode
        self.ui.progress_widget.set_phase(self.ui.progress_widget.PHASE_FINALIZE)

        self.ui.progress_widget.push("Running finalizing pass")
        try:
            self._visit_tree_r(parent, lambda child: child.finalize(), "Finalizing")
        except Exception, e:
            self.ui.progress_widget.logger.error("Error while finalizing. Aborting.")
            return
        finally:
            self.ui.progress_widget.pop()

        self.ui.progress_widget.logger.info("Publish Complete!")

        # make the publish button say close
        self.ui.publish.setText("Close")
        self._close_ui_on_publish_click = True


    def _visit_tree_r(self, parent, action, action_name):
        """
        Recursive visitor helper function that descends the tree
        """
        number_true_return_values = 0

        for child_index in xrange(parent.childCount()):
            child = parent.child(child_index)
            if child.enabled:
                if action_name:
                    self.ui.progress_widget.push(
                        "%s %s" % (action_name, child),
                        child.icon,
                        child.get_publish_instance()
                    )
                try:
                    # process this node
                    status = action(child)  # eg. child.validate(), child.publish() etc.
                    if not status:
                        number_true_return_values += 1

                    # kick progress bar
                    self.ui.progress_widget.increment_progress()

                    # now process all children
                    number_true_return_values += self._visit_tree_r(
                        child,
                        action,
                        action_name
                    )
                finally:
                    if action_name:
                        self.ui.progress_widget.pop()
        return number_true_return_values

    def _on_drop(self, files):
        """
        When someone drops stuff into the publish.
        """
        # make sure we switch main mode to the publish screen
        self.ui.main_stack.setCurrentIndex(self.PUBLISH_SCREEN)
        # add files and rebuild tree
        self._plugin_manager.add_external_files(files)
        self.ui.items_tree.build_tree()

    def is_first_launch(self):
        """
        Returns true if this is the first time UI is being launched
        """
        ui_launched = self._settings_manager.retrieve("ui_launched", False, self._settings_manager.SCOPE_ENGINE)
        if ui_launched == False:
            # store in settings that we now have launched
            self._settings_manager.store("ui_launched", True, self._settings_manager.SCOPE_ENGINE)

        return not ui_launched

    def show_help_popup(self):
        """
        Someone clicked the show help screen action
        """
        app = sgtk.platform.current_bundle()
        help_pix = [
            QtGui.QPixmap(":/tk_multi_publish2/help_1.png"),
            QtGui.QPixmap(":/tk_multi_publish2/help_2.png"),
            QtGui.QPixmap(":/tk_multi_publish2/help_3.png"),
            QtGui.QPixmap(":/tk_multi_publish2/help_4.png")
        ]
        help_screen.show_help_screen(self.window(), app, help_pix)

