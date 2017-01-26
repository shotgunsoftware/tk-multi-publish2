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

from .processing import ValidationFailure, PublishFailure

# import frameworks
#shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
settings = sgtk.platform.import_framework("tk-framework-shotgunutils", "settings")
help_screen = sgtk.platform.import_framework("tk-framework-qtwidgets", "help_screen")
#overlay_widget = sgtk.platform.import_framework("tk-framework-qtwidgets", "overlay_widget")
#task_manager = sgtk.platform.import_framework("tk-framework-shotgunutils", "task_manager")
#shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")

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


        # set up the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # make sure the splitter expands the detail area only
        self.ui.splitter.setStretchFactor(0, 0)
        self.ui.splitter.setStretchFactor(1, 1)

        # set up tree view to look slick
        self.ui.items_tree.setRootIsDecorated(False)
        self.ui.items_tree.setItemsExpandable(False)
        self.ui.items_tree.setIndentation(20)


        self.ui.frame.something_dropped.connect(self._on_drop)


        self.ui.reload.clicked.connect(self.do_reload)
        self.do_reload()





    def do_reload(self):
        """

        @return:
        """
        self.ui.items_tree.clear()

        item = QtGui.QTreeWidgetItem(self.ui.items_tree)

        child_item = QtGui.QTreeWidgetItem(item)

        pd = Item(self)
        pd.set_header("foo bar baz")
        pd.set_mode(Item.ITEM)
        #pd.set_status(pd.VALIDATION_ERROR)

        pd2 = Item(self)
        pd2.set_header("yeah baby")
        pd2.set_mode(Item.PLUGIN)
        #pd2.set_status(pd2.PROCESSING)

        self.ui.items_tree.addTopLevelItem(item)

        self.ui.items_tree.setItemWidget(item, 0, pd)
        self.ui.items_tree.setItemWidget(child_item, 0, pd2)

        self.ui.items_tree.expandItem(item)


    def _on_drop(self, data):
        """
        When someone drops stuff into the publish.
        @param data:
        @return:
        """
        print "DROP %s" % data


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








