# Copyright (c) 2026 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk.
"""Hook that defines how the command/action to show the publish dialog is displayed.

The output of methods in this hook are used as follows when calling
`.sgtk.platform.Application.register_command`::

    app.register_command(
        app.execute_hook_method("display_hook", "menu_name"),
        ...,
        properties=app.execute_hook_method("display_hook", "menu_properties"),
    )
"""

import os
import re
from typing import Any

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class DisplayHook(HookBaseClass):
    """Hook that defines how the action to show the publish dialog is displayed."""

    @property
    def settings(self) -> dict[str, Any]:
        """Return the settings that are available for this hook."""
        return self.parent.get_setting("display").get("settings") or {}

    @property
    def action_name(self) -> str:
        """Create text used when inferring to the "Publish" action in the GUI."""
        return self.parent.get_setting("display_action_name")

    @property
    def button_name(self) -> str:
        """Create the label text used when for "Publish" button."""
        return self.action_name

    @property
    def menu_name(self) -> str:
        """Create the command name used when registering the show dialog command."""
        return f"{self.parent.get_setting('display_name')}..."

    @property
    def menu_properties(self) -> dict[str, Any]:
        """Create the properties used when registering the show dialog command.

        See expected property details at `.sgtk.platform.Application.register_command`.
        """
        display_name = self.parent.get_setting("display_name")
        command_name = re.sub(r"[^0-9a-zA-Z]+", "_", display_name.lower())

        return {
            "short_name": command_name,
            "description": "Publishing of data to Flow Production Tracking",
            "icons": {
                "dark": {
                    "png": os.path.join(self.parent.disk_location, "icon_256_dark.png")
                }
            },
        }
