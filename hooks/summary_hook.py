# Copyright (c) 2026 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk.
"""Hook that defines the summary overlay content and display details."""

from typing import Any

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class SummaryHook(HookBaseClass):
    """Hook that defines the summary overlay content and display details."""

    @property
    def settings(self) -> dict[str, Any]:
        """Return the settings that are available for this hook."""
        return self.parent.get_setting("summary").get("settings") or {}

    def no_items_error(self, summary_overlay) -> dict[str, Any]:
        """Return UI values for the no items collected summary state."""
        return summary_overlay.show_summary(
            ":/tk_multi_publish2/publish_failed.png",
            # Hardcoding line break so the message displays on 2 lines.
            # Usage of label's own word wrap displays the message below on 3 lines.
            # NOTE: Can't manually break line when using <p></p>
            "Could not find any\nitems to publish.",
            "For more details, <b><u>click here</u></b>.",
        )

    def success(self, summary_overlay) -> dict[str, Any]:
        """Return UI values for the publish success summary state."""
        return summary_overlay.show_summary(
            ":/tk_multi_publish2/publish_complete.png",
            "Publish\nComplete",
            "For more details, <b><u>click here</u></b>.",
            publish_again_text="To publish again, <b><u>click here</u></b>.",
        )

    def fail(self, summary_overlay) -> dict[str, Any]:
        """Return UI values for the publish fail summary state."""
        return summary_overlay.show_summary(
            ":/tk_multi_publish2/publish_failed.png",
            "Publish\nFailed!",
            "For more details, <b><u>click here</u></b>.",
        )

    def loading(self, summary_overlay) -> dict[str, Any]:
        """Return UI values for the loading summary state."""
        return summary_overlay.show_summary(
            ":/tk_multi_publish2/overlay_loading.png",
            "Loading and processing",
            "Hold tight while we analyze your data",
        )
