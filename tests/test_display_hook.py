# Copyright (c) 2026 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk.
import os

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa


class TestDisplayHook(PublishApiTestBase):
    def test_attributes_exist(self):
        from sgtk import Hook

        assert hasattr(self.app, "display_hook")
        assert isinstance(self.app.display_hook, Hook)
        for prop in ("action_name", "button_name", "menu_name", "menu_properties"):
            assert hasattr(self.app.display_hook, prop)

    def test_matches_v2_10_7(self):
        """Test new display hook properties match same values from on v2.10.7 tag.

        This ensures drop-in compatibility with existing code and configurations.
        """
        app = self.app

        # tk-multi-publish2/app.py:MultiPublish2.init_app()
        from tank.util import sgre as re

        display_name = app.get_setting("display_name")
        command_name = display_name.lower()
        command_name = re.sub(r"[^0-9a-zA-Z]+", "_", command_name)
        menu_caption = "%s..." % display_name
        menu_options = {
            "short_name": command_name,
            "description": "Publishing of data to Flow Production Tracking",
            "icons": {
                "dark": {"png": os.path.join(app.disk_location, "icon_256_dark.png")}
            },
        }
        # self.engine.register_command(menu_caption, cb, menu_options)
        assert app.display_hook.menu_name == menu_caption
        assert app.display_hook.menu_properties == menu_options

        # tk-multi-publish2/python/tk_multi_publish2/dialog.py:AppDialog.__init__()
        display_action_name = app.get_setting("display_action_name")
        # self._display_action_name = self._bundle.get_setting("display_action_name")
        # self.ui.publish.setText(self._display_action_name)
        assert app.display_hook.action_name == display_action_name
        assert app.display_hook.button_name == display_action_name
