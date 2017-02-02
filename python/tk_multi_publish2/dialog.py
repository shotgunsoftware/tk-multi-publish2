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
from .item import Item
from .tree_item import PublishTreeWidgetItem, PublishTreeWidgetTask, PublishTreeWidgetPlugin

from .publish_logging import PublishLogWrapper

from .processing import ValidationFailure, PublishFailure

# import frameworks
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")
help_screen = sgtk.platform.import_framework("tk-framework-qtwidgets", "help_screen")

logger = sgtk.platform.get_logger(__name__)

class AppDialog(QtGui.QWidget):
    """
    Main dialog window for the App
    """

    (ITEM_CENTRIC, PLUGIN_CENTRIC) = range(2)

    (SUMMARY_DETAILS, TASK_DETAILS, PLUGIN_DETAILS, ITEM_DETAILS, BLANK_DETAILS) = range(5)

    (DETAILS_TAB, PROGRESS_TAB) = range(2)


    def __init__(self, parent=None):
        """
        Constructor
        
        :param parent:          The parent QWidget for this control
        """
        QtGui.QWidget.__init__(self, parent)

        # create a settings manager where we can pull and push prefs later
        # prefs in this manager are shared
        self._settings_manager = settings.UserSettings(sgtk.platform.current_bundle())

        self._bundle = sgtk.platform.current_bundle()

        # set up the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # make sure the splitter expands the detail area only
        self.ui.splitter.setStretchFactor(0, 0)
        self.ui.splitter.setStretchFactor(1, 1)

        # give tree view 360 width, rest to details pane
        # note: value of second option does not seem to matter (as long as it's there)
        self.ui.splitter.setSizes([360, 100])

        # set up tree view to look slick
        self.ui.items_tree.setIndentation(20)

        # drag and drop
        self.ui.frame.something_dropped.connect(self._on_drop)

        # create a special logger for progress
        self._log_wrapper = PublishLogWrapper(self.ui.log_tree)

        # buttons
        self.ui.swap.clicked.connect(self._swap_view)
        self.ui.validate.clicked.connect(self.do_validate)
        self.ui.publish.clicked.connect(self.do_publish)


        self._menu = QtGui.QMenu()
        self._actions = []
        self.ui.options.setMenu(self._menu)
        self._refresh_action = QtGui.QAction("Refresh", self)
        self._refresh_action.setIcon(QtGui.QIcon(QtGui.QPixmap(":/tk_multi_publish2/reload.png")))
        self._refresh_action.triggered.connect(self._refresh)
        self._menu.addAction(self._refresh_action)

        self._separator_1= QtGui.QAction(self)
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
        self._check_all_action.triggered.connect(lambda : self._check_all(True))
        self._menu.addAction(self._check_all_action)

        self._uncheck_all_action = QtGui.QAction("Unckeck All", self)
        self._uncheck_all_action.triggered.connect(lambda : self._check_all(False))
        self._menu.addAction(self._uncheck_all_action)

        # when the description is updated
        self.ui.summary_comments.textChanged.connect(self._on_publish_comment_change)


        # selection in tree view
        self.ui.items_tree.itemSelectionChanged.connect(self._update_details_from_selection)
        self.ui.reversed_items_tree.itemSelectionChanged.connect(self._update_details_from_selection)

        # thumbnails
        self.ui.summary_thumbnail.screen_grabbed.connect(self._update_item_thumbnail)
        self.ui.item_thumbnail.screen_grabbed.connect(self._update_item_thumbnail)

        # mode
        self._display_mode = self.ITEM_CENTRIC

        # currently displayed item
        self._current_item = None

        # start up our plugin manager
        self._plugin_manager = PluginManager(self._log_wrapper.logger)

        # start it up
        self._refresh()


    def _update_details_from_selection(self):
        """
        Makes sure that the right hand side
        details section reflects the selected item
        in the left hand side tree.
        """
        if self._display_mode == self.ITEM_CENTRIC:
            items = self.ui.items_tree.selectedItems()
        else:
            items = self.ui.reversed_items_tree.selectedItems()

        if len(items) == 0:
            tree_item = None
        else:
            tree_item = items[0]

        # make sure we are focused on the details tab
        self.ui.right_tabs.setCurrentIndex(self.DETAILS_TAB)

        if tree_item is None:
            self.ui.details_stack.setCurrentIndex(self.BLANK_DETAILS)

        elif tree_item.parent() is None and isinstance(tree_item, PublishTreeWidgetItem):
            # top level item
            self._create_summary_details(tree_item.item)

        elif isinstance(tree_item, PublishTreeWidgetItem):
            self._create_item_details(tree_item.item)

        elif isinstance(tree_item, PublishTreeWidgetTask):
            self._create_task_details(tree_item.task)

        elif isinstance(tree_item, PublishTreeWidgetPlugin):
            self._create_plugin_details(tree_item.plugin)

        else:
            raise TankError("Unknown selection")

    def _on_publish_comment_change(self):
        """
        Callback when someone types in the
        publish comments box in the overview details pane
        """
        comments = self.ui.summary_comments.toPlainText()
        if not self._current_item:
            raise TankError("No current item set!")
        self._current_item.set_description(comments)

    def _on_summary_thumbnail_captured(self, pixmap):
        """
        Callback when a thumbnail is captured
        @param pixmap:
        @return:
        """
        if not self._current_item:
            raise TankError("No current item set!")
        self._current_item.set_thumbnail_pixmap(pixmap)

    def _update_item_thumbnail(self, pixmap):
        """
        Update the currently selected item with the given
        thumbnail pixmap
        """
        if not self._current_item:
            raise TankError("No current item set!")
        self._current_item.set_thumbnail_pixmap(pixmap)

    def _create_summary_details(self, item):

        self._current_item = item
        self.ui.details_stack.setCurrentIndex(self.SUMMARY_DETAILS)
        self.ui.summary_icon.setPixmap(item.icon_pixmap)
        self.ui.summary_comments.setPlainText(item.description)
        self.ui.summary_thumbnail.set_thumbnail(item.thumbnail_pixmap)
        self.ui.summary_header.setText("Publish summary for %s" % item.name)
        self.ui.summary_context.setText(str(self._bundle.context))


    def _create_item_details(self, item):

        self._current_item = item
        self.ui.details_stack.setCurrentIndex(self.ITEM_DETAILS)

        self.ui.item_icon.setPixmap(item.icon_pixmap)
        self.ui.item_name.setText(item.name)
        self.ui.item_type.setText(item.display_type)
        self.ui.item_thumbnail.set_thumbnail(item.thumbnail_pixmap)

        self.ui.item_settings.set_static_data(
            [(p, item.properties[p]) for p in item.properties]
        )

    def _create_task_details(self, task):

        self._current_item = None
        self.ui.details_stack.setCurrentIndex(self.TASK_DETAILS)

        self.ui.task_icon.setPixmap(task.plugin.icon_pixmap)
        self.ui.task_name.setText(task.plugin.name)

        self.ui.task_description.setText(task.plugin.description)

        self.ui.task_settings.set_data(task.settings.values())


    def _create_plugin_details(self, plugin):

        self._current_item = None
        self.ui.details_stack.setCurrentIndex(self.PLUGIN_DETAILS)
        self.ui.plugin_icon.setPixmap(plugin.icon_pixmap)

        self.ui.plugin_name.setText(plugin.name)

        self.ui.plugin_description.setText(plugin.description)
        self.ui.plugin_settings.set_data(plugin.settings.values())



    def _refresh(self):

        self._reload_plugin_scan()
        self._build_tree()
        self._select_top_items()

    def _select_top_items(self):

        # select the top item
        if self.ui.items_tree.topLevelItemCount() > 0:
            self.ui.items_tree.setCurrentItem(
                self.ui.items_tree.topLevelItem(0)
            )

        # select the top item
        if self.ui.reversed_items_tree.topLevelItemCount() > 0:
            self.ui.reversed_items_tree.setCurrentItem(
                self.ui.reversed_items_tree.topLevelItem(0)
            )

    def _collapse_tree(self):
        """
        Contract all the nodes in the currently active left hand side tree
        """
        if self._display_mode == self.ITEM_CENTRIC:
            for item_index in xrange(self.ui.items_tree.topLevelItemCount()):
                item = self.ui.items_tree.topLevelItem(item_index)
                self.ui.items_tree.collapseItem(item)
        else:
            for item_index in xrange(self.ui.reversed_items_tree.topLevelItemCount()):
                item = self.ui.reversed_items_tree.topLevelItem(item_index)
                self.ui.reversed_items_tree.collapseItem(item)

    def _expand_tree(self):
        """
        Expand all the nodes in the currently active left hand side tree
        """
        if self._display_mode == self.ITEM_CENTRIC:
            for item_index in xrange(self.ui.items_tree.topLevelItemCount()):
                item = self.ui.items_tree.topLevelItem(item_index)
                self.ui.items_tree.expandItem(item)
        else:
            for item_index in xrange(self.ui.reversed_items_tree.topLevelItemCount()):
                item = self.ui.reversed_items_tree.topLevelItem(item_index)
                self.ui.reversed_items_tree.expandItem(item)

    def _check_all(self, checked):
        """
        Check all boxes in the currently active tree
        """
        def _check_r(parent):
            for child_index in xrange(parent.childCount()):
                child = parent.child(child_index)
                child.checkbox.setChecked(checked)
                _check_r(child)

        if self._display_mode == self.ITEM_CENTRIC:
            parent = self.ui.items_tree.invisibleRootItem()
        else:
            parent = self.ui.reversed_items_tree.invisibleRootItem()

        _check_r(parent)

    def _swap_view(self):
        """
        Swaps left hand side tree views between
        item centric and plugin centric modes.
        """
        if self._display_mode == self.ITEM_CENTRIC:
            self._display_mode = self.PLUGIN_CENTRIC
            self.ui.items_tree_stack.setCurrentIndex(self.PLUGIN_CENTRIC)
        else:
            self._display_mode = self.ITEM_CENTRIC
            self.ui.items_tree_stack.setCurrentIndex(self.ITEM_CENTRIC)
        self._update_details_from_selection()


    def _build_item_tree_r(self, parent, item):
        """
        Build the tree of items
        """
        if len(item.tasks) == 0 and len(item.children) == 0:
            # orphan. Don't create it
            return None

        ui_item = PublishTreeWidgetItem(item, parent)
        ui_item.setExpanded(True)

        for task in item.tasks:
            task = PublishTreeWidgetTask(task, ui_item)

        for child in item.children:
            self._build_item_tree_r(ui_item, child)

        return ui_item

    def _build_plugin_tree_r(self, parent, plugin):
        """
        Build the tree of plugins
        """

        if len(plugin.tasks) == 0:
            # orphan. Don't create it
            return None

        ui_item = PublishTreeWidgetPlugin(plugin, parent)
        ui_item.setExpanded(True)

        for task in plugin.tasks:
            item = PublishTreeWidgetItem(task.item, ui_item)

        return ui_item


    def _build_tree(self):
        """
        Rebuilds the lefthand side tree
        """
        # first build the items tree
        self.ui.items_tree.clear()
        for item in self._plugin_manager.top_level_items:
            ui_item = self._build_item_tree_r(self.ui.items_tree, item)
            if ui_item:
                self.ui.items_tree.addTopLevelItem(ui_item)

        # now build the reverse one
        self.ui.reversed_items_tree.clear()
        for item in self._plugin_manager.plugins:
            ui_item = self._build_plugin_tree_r(self.ui.reversed_items_tree, item)
            if ui_item:
                self.ui.reversed_items_tree.addTopLevelItem(ui_item)


    def _reload_plugin_scan(self):
        """

        """
        # run the hooks
        self._plugin_manager = PluginManager(self._log_wrapper.logger)


    def do_validate(self):
        """
        Perform a full validation
        """

        # make sure we swap the tree
        if self._display_mode != self.ITEM_CENTRIC:
            self._swap_view()

        # and expand it
        self._expand_tree()

        # flip right hand side to show the logs
        self.ui.right_tabs.setCurrentIndex(self.PROGRESS_TAB)

        parent = self.ui.items_tree.invisibleRootItem()

        self._log_wrapper.push("Running Validation pass")

        # set all nodes to "ready to go"
        def _begin_process_r(parent):
            for child_index in xrange(parent.childCount()):
                child = parent.child(child_index)
                child.begin_process()
                _begin_process_r(child)
        _begin_process_r(parent)

        try:
            num_issues = self._visit_tree_r(parent, lambda child: child.validate(), "Validating")
        finally:
            self._log_wrapper.pop()
            if num_issues > 0:
                self._log_wrapper.logger.warning("Validation Complete. %d issues reported." % num_issues)
            else:
                self._log_wrapper.logger.info("Validation Complete. All checks passed.")

    def do_publish(self):

        # make sure we swap the tree
        if self._display_mode != self.ITEM_CENTRIC:
            self._swap_view()

        # and expand it
        self._expand_tree()

        self.ui.right_tabs.setCurrentIndex(self.PROGRESS_TAB)

        parent = self.ui.items_tree.invisibleRootItem()

        # set all nodes to "ready to go"
        self._visit_tree_r(parent, lambda child: child.begin_process())

        self._log_wrapper.push("Running validation pass")

        try:
            self._visit_tree_r(parent, lambda child: child.validate(), "Validating")
        finally:
            self._log_wrapper.pop()

        self._log_wrapper.push("Running publishing pass")
        try:
            self._visit_tree_r(parent, lambda child: child.publish(), "Publishing")
        finally:
            self._log_wrapper.pop()

        self._log_wrapper.push("Running finalizing pass")
        try:
            self._visit_tree_r(parent, lambda child: child.finalize(), "Finalizing")
        finally:
            self._log_wrapper.pop()

        self._log_wrapper.logger.info("Publish Complete!")


    def _visit_tree_r(self, parent, action, action_name=None):

        num_problems = 0

        for child_index in xrange(parent.childCount()):
            child = parent.child(child_index)
            if child.enabled:
                if action_name:
                    self._log_wrapper.push("%s %s" % (action_name, child), child.icon)
                try:
                    status = action(child) # eg. child.validate(), child.publish() etc.
                    if not status:
                        num_problems += 1
                    num_problems += self._visit_tree_r(child, action, action_name)
                finally:
                    if action_name:
                        self._log_wrapper.pop()
        return num_problems

    def _on_drop(self, files):
        """
        When someone drops stuff into the publish.
        """
        self._plugin_manager.add_external_files(files)
        self._build_tree()

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

