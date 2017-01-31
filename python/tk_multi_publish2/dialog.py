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

        # set up tree view to look slick
        self.ui.items_tree.setRootIsDecorated(False)
        #self.ui.items_tree.setItemsExpandable(False)
        self.ui.items_tree.setIndentation(20)

        # drag and drop
        self.ui.frame.something_dropped.connect(self._on_drop)

        # buttons
        self.ui.reload.clicked.connect(self._on_refresh_clicked)
        self.ui.swap.clicked.connect(self._on_swap_clicked)
        self.ui.validate.clicked.connect(self.do_validate)
        self.ui.publish.clicked.connect(self.do_publish)

        # selection in tree view

        self.ui.items_tree.itemSelectionChanged.connect(self._on_tree_selection_change)

        # mode
        self._display_mode = self.ITEM_CENTRIC

        # start up our plugin manager
        self._plugin_manager = PluginManager()

        # start it up
        self._on_refresh_clicked()



    def _build_item_tree_r(self, parent, item):

        ui_item = PublishTreeWidgetItem(item, parent)
        ui_item.setExpanded(True)

        for task in item.tasks:
            task = PublishTreeWidgetTask(task, ui_item)

        for child in item.children:
            self._build_item_tree_r(ui_item, child)

        return ui_item

    def _build_plugin_tree_r(self, parent, plugin):

        ui_item = PublishTreeWidgetPlugin(plugin, parent)
        ui_item.setExpanded(True)

        for task in plugin.tasks:
            item = PublishTreeWidgetItem(task.item, ui_item)

        return ui_item

    def _on_tree_selection_change(self):
        logger.debug("Tree selection changed!")
        items = self.ui.items_tree.selectedItems()
        logger.debug("items: %s" % items)
        if len(items) == 0:
            selected_item = None
        else:
            selected_item = items[0]

        logger.debug("selected: %s" % selected_item)

        print selected_item.parent()
        print self.ui.items_tree.invisibleRootItem()

        if selected_item is None:
            self.ui.details_stack.setCurrentIndex(self.BLANK_DETAILS)

        elif selected_item.parent() is None and isinstance(selected_item, PublishTreeWidgetItem):
            # top level item
            self._create_summary_details(selected_item.item)

        elif isinstance(selected_item, PublishTreeWidgetItem):
            self._create_item_details(selected_item.item)

        elif isinstance(selected_item, PublishTreeWidgetTask):
            self._create_task_details(selected_item.task)

        elif isinstance(selected_item, PublishTreeWidgetPlugin):
            self._create_plugin_details(selected_item.plugin)

        else:
            raise TankError("Uknownn selection")


    def _create_summary_details(self, item):
        self.ui.details_stack.setCurrentIndex(self.SUMMARY_DETAILS)

    def _create_item_details(self, item):
        self.ui.details_stack.setCurrentIndex(self.ITEM_DETAILS)

    def _create_task_details(self, task):
        self.ui.details_stack.setCurrentIndex(self.TASK_DETAILS)

    def _create_plugin_details(self, plugin):
        self.ui.details_stack.setCurrentIndex(self.PLUGIN_DETAILS)





    def _on_refresh_clicked(self):

        self._do_reload()
        self._build_tree()


    def _on_swap_clicked(self):

        if self._display_mode == self.ITEM_CENTRIC:
            self._display_mode = self.PLUGIN_CENTRIC
        else:
            self._display_mode = self.ITEM_CENTRIC

        self._build_tree()


    def _build_tree(self):

        self.ui.items_tree.clear()

        if self._display_mode == self.ITEM_CENTRIC:
            for item in self._plugin_manager.top_level_items:
                ui_item = self._build_item_tree_r(self.ui.items_tree, item)
                self.ui.items_tree.addTopLevelItem(ui_item)

        else:
            for item in self._plugin_manager.plugins:
                ui_item = self._build_plugin_tree_r(self.ui.items_tree, item)
                self.ui.items_tree.addTopLevelItem(ui_item)

    def _do_reload(self):
        """

        @return:
        """
        # run the hooks
        self._plugin_manager = PluginManager()




    def do_validate(self):
        self.log_debug("Validate")

    def do_publish(self):
        self.log_debug("Publish")







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








