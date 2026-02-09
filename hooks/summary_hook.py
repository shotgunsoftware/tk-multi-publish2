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

    FALLBACK_SETTINGS = {
        "no_item_error": {
            "icon_path": ":/tk_multi_publish2/publish_failed.png",
            # Hardcoding line break so the message displays on 2 lines.
            # Usage of label's own word wrap displays the message below on 3 lines.
            # NOTE: Can't manually break line when using <p></p>
            "label_text": "Could not find any\nitems to publish.",
            "info_text": "For more details, <b><u>click here</u></b>.",
            "publish_again_text": "",
        },
        "success": {
            "icon_path": ":/tk_multi_publish2/publish_complete.png",
            "label_text": "Publish\nComplete",
            "info_text": "For more details, <b><u>click here</u></b>.",
            "publish_again_text": "To publish again, <b><u>click here</u></b>.",
        },
        "fail": {
            "icon_path": ":/tk_multi_publish2/publish_failed.png",
            "label_text": "Publish\nFailed!",
            "info_text": "For more details, <b><u>click here</u></b>.",
            "publish_again_text": "",
        },
        "loading": {
            "icon_path": ":/tk_multi_publish2/overlay_loading.png",
            "label_text": "Loading and processing",
            "info_text": "Hold tight while we analyze your data",
            "publish_again_text": "",
        },
    }
    """Fallback settings to use for `.show_using_settings`, uses v2.10.7 values."""

    @property
    def settings(self) -> dict[str, Any]:
        """Return the settings that are available for this hook."""
        return self.parent.get_setting("summary").get("settings") or {}

    def show_using_settings(self, key, summary_overlay) -> dict[str, Any]:
        """Return UI values for the no items collected summary state."""
        settings = self.settings.get(key, {})
        fallback = self.FALLBACK_SETTINGS.get(key, {})
        return summary_overlay.show_summary(
            settings.get("icon_path", fallback["icon_path"]),
            settings.get("label_text", fallback["label_text"]),
            settings.get("info_text", fallback["info_text"]),
            publish_again_text=settings.get(
                "publish_again_text", fallback["publish_again_text"]
            ),
        )

    def no_items_error(self, summary_overlay) -> dict[str, Any]:
        """Return UI values for the no items collected summary state."""
        return self.show_using_settings("no_item_error", summary_overlay)

    def success(self, summary_overlay) -> dict[str, Any]:
        """Return UI values for the publish success summary state."""
        return self.show_using_settings("success", summary_overlay)

    def fail(self, summary_overlay) -> dict[str, Any]:
        """Return UI values for the publish fail summary state."""
        return self.show_using_settings("fail", summary_overlay)

    def loading(self, summary_overlay) -> dict[str, Any]:
        """Return UI values for the loading summary state."""
        return self.show_using_settings("loading", summary_overlay)
