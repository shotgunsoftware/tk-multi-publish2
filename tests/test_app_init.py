# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from unittest.mock import MagicMock
import sys

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa


class TestAppNonUiInit(PublishApiTestBase):
    """
    Checks that the app starts and exposes the publish API without loading UI
    modules or registering menu commands when the engine has no UI.
    """

    def test_package_does_not_eagerly_import_publish_tree_widget(self):
        """
        Importing the app package must not pull in the publish tree widget,
        so batch / non-UI engines can use the publish API without Qt UI imports.
        """
        pkg = self.app.import_module("tk_multi_publish2")
        self.assertFalse(hasattr(pkg, "publish_tree_widget"))
        widget_module_name = "%s.publish_tree_widget" % pkg.__name__
        self.assertNotIn(widget_module_name, sys.modules)

    def test_publish_api_available_in_batch_mode(self):
        """
        The publish API must be usable regardless of whether the host engine exposes UI.
        """
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.app.util)
        self.assertIsNotNone(self.app.base_hooks)
        self.assertIsNotNone(self.app.create_publish_manager())

    def test_menu_command_follows_engine_has_ui(self):
        menu_caption = "%s..." % self.app.get_setting("display_name")
        if self.engine.has_ui:
            self.assertIn(menu_caption, self.engine.commands)
        else:
            self.assertNotIn(menu_caption, self.engine.commands)

    def _make_init_app_mock(self, has_ui):
        app_class = type(self.app)
        hook_setting = app_class.CONFIG_PRE_PUBLISH_HOOK_PATH
        app = MagicMock()
        app.engine = MagicMock()
        app.engine.has_ui = has_ui
        app.CONFIG_PRE_PUBLISH_HOOK_PATH = hook_setting
        app.get_setting = MagicMock(
            side_effect=lambda key: {
                "display_name": "Publish",
                "modal": False,
                hook_setting: "pre_publish",
            }[key]
        )
        tk_multi_publish2 = MagicMock()
        app.import_module = MagicMock(return_value=tk_multi_publish2)
        app.create_hook_instance = MagicMock()
        app.disk_location = self.app.disk_location
        return app_class, app, tk_multi_publish2

    def test_init_app_does_not_register_command_without_ui(self):
        app_class, app, _tk_multi_publish2 = self._make_init_app_mock(has_ui=False)
        app_class.init_app(app)
        app.engine.register_command.assert_not_called()

    def test_init_app_registers_command_with_ui(self):
        app_class, app, tk_multi_publish2 = self._make_init_app_mock(has_ui=True)
        app_class.init_app(app)
        app.engine.register_command.assert_called_once()
        menu_caption, callback, menu_options = app.engine.register_command.call_args[0]
        self.assertEqual(menu_caption, "Publish...")
        self.assertEqual(menu_options["short_name"], "publish")
        callback()
        tk_multi_publish2.show_dialog.assert_called_once_with(app)
