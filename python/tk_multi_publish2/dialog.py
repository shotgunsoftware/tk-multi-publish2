# Copyright (c) 2015 Shotgun Software Inc.
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

from .plugin_manager import PluginManager
from .publish_details import PublishDetails

from .errors import ValidationFailure, PublishFailure

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

        self.ui.publish.clicked.connect(self.do_publish)
        self.ui.validate.clicked.connect(self.do_validation)
        self.ui.reload.clicked.connect(self.do_reload)

        self.do_reload()


    def do_reload(self):

        self._plugins = []

        self._plugin_manager = PluginManager()

        # first create the special mandatory ui
        (self._publish_item, self._publish_details) = self.ui.plugin_selector.create_plugin(PublishDetails)

        # test of fixed sg header thingie
        self._publish_item.set_header(
            "Shotgun Details",
            "Information about your publish"
        )
        self._publish_item.set_icon(QtGui.QPixmap(":/tk_multi_publish2/shotgun.png"))
        self._publish_item.select()


        # now load up all plugins from hooks
        for plugin in self._plugin_manager.plugins:
            (item, details) = self.ui.plugin_selector.create_plugin()

            item.set_header(
                plugin.title,
                plugin.summary
            )

            item.set_icon(plugin.icon_pixmap)

            details.set_description(plugin.description)


            # tell item ui to render settings UI
            details.add_settings(plugin.required_settings)

            # analyze the scene
            tasks = plugin.scan_scene(
                details.get_logger(),
                runtime_settings=details.get_settings()
            )
            for task in tasks:
                item.add_task(task)

            self._plugins.append(
                {"item": item, "details": details, "plugin": plugin}
            )

        self.ui.plugin_selector.finalize_list()

    def do_validation(self):

        logger.debug("Starting validation")

        for plugin in self._plugins:

            self.ui.plugin_selector.select(plugin["item"])

            all_success = True

            for task in plugin["item"].get_tasks():

                try:
                    plugin["plugin"].validate(
                        plugin["details"].get_logger(),
                        task,
                        runtime_settings=plugin["details"].get_settings()
                    )
                except ValidationFailure:
                    validation_ok = False
                else:
                    validation_ok = True

                all_success &= validation_ok

                if validation_ok:
                    plugin["item"].set_task_mode(task, plugin["item"].VALIDATION_COMPLETE)
                else:
                    plugin["item"].set_task_mode(task, plugin["item"].VALIDATION_ERROR)

            if all_success:
                plugin["item"].set_mode(plugin["item"].VALIDATION_COMPLETE)
            else:
                plugin["item"].set_mode(plugin["item"].VALIDATION_ERROR)


    def do_publish(self):

        self.do_validation()

        logger.debug("Starting publish")

        for plugin in self._plugins:

            self.ui.plugin_selector.select(plugin["item"])

            all_success = True

            for task in plugin["item"].get_tasks():

                try:
                    plugin["plugin"].publish(
                        plugin["details"].get_logger(),
                        task,
                        runtime_settings=plugin["details"].get_settings()
                    )
                except PublishFailure:
                    publish_ok = False
                else:
                    publish_ok = True

                all_success &= publish_ok
                if publish_ok:
                    plugin["item"].set_task_mode(task, plugin["item"].PUBLISH_COMPLETE)
                else:
                    plugin["item"].set_task_mode(task, plugin["item"].PUBLISH_ERROR)

            if all_success:
                plugin["item"].set_mode(plugin["item"].PUBLISH_COMPLETE)
            else:
                plugin["item"].set_mode(plugin["item"].PUBLISH_ERROR)


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








