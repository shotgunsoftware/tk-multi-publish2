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
from .tree_item import PublishTreeWidgetItem, PublishTreeWidgetConnection

from .processing import ValidationFailure, PublishFailure

# import frameworks
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")
help_screen = sgtk.platform.import_framework("tk-framework-qtwidgets", "help_screen")

logger = sgtk.platform.get_logger(__name__)

class AppDialog(QtGui.QWidget):
    """
    Main dialog window for the App
    """

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
        #self.ui.items_tree.setRootIsDecorated(False)
        #self.ui.items_tree.setItemsExpandable(False)
        self.ui.items_tree.setIndentation(20)

        # drag and drop
        self.ui.frame.something_dropped.connect(self._on_drop)

        # buttons
        self.ui.reload.clicked.connect(self.do_reload)
        self.ui.validate.clicked.connect(self.do_validate)
        self.ui.publish.clicked.connect(self.do_publish)

        # start up our plugin manager
        self._plugin_manager = PluginManager()

        # start it up
        self.do_reload()



    def _build_tree_r(self, parent, item):

        ui_item = PublishTreeWidgetItem(item, parent)
        ui_item.setExpanded(True)

        for connection in item.connections:
            connection = PublishTreeWidgetConnection(connection, ui_item)

        for child in item.children:
            self._build_tree_r(ui_item, child)



        return ui_item

    def do_reload(self):
        """

        @return:
        """
        self.ui.items_tree.clear()

        # run the hooks
        self._plugin_manager.collect()



        for item in self._plugin_manager.top_level_items:

            ui_item = self._build_tree_r(self.ui.items_tree, item)
            self.ui.items_tree.addTopLevelItem(ui_item)






    def do_validate(self):
        self.log_debug("Validate")

    def do_publish(self):
        self.log_debug("Publish")










    def _on_drop(self, data):
        """
        When someone drops stuff into the publish.
        """
        self._bundle.add_external_files(data)
        self.do_reload()

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








