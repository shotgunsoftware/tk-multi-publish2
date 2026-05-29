# Copyright (c) 2025 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
from __future__ import annotations  # needed for Houdini 19.5 support

from types import ModuleType

import sgtk
from sgtk.platform.qt import QtGui

HookBaseClass = sgtk.get_hook_baseclass()


class PrePublishHook(HookBaseClass):
    """
    This hook defines logic to be executed before showing the publish
    dialog. There may be conditions that need to be checked before allowing
    the user to proceed to publishing.
    """

    def _get_flow_module(self) -> ModuleType:
        """
        Load the Flow AM framework and return the flow module.
        Caches the module as a member variable to avoid repeated framework loading.

        :return: The flow module from tk-framework-flowam
        """
        if not hasattr(self, "_flow_module"):
            flow_am_fw = self.load_framework("tk-framework-flowam_v1.x.x")
            self._flow_module = flow_am_fw.import_module("flow")
        return self._flow_module

    def _get_draft_id(self) -> str | None:
        """
        Get the current draft ID from the Flow AM context.

        :return: The draft ID or None if not available
        """
        flow_module = self._get_flow_module()
        return flow_module.asset_management.FlowContext.draft_id

    def validate(self):
        """
        Returns True if the user can proceed to publish. Override this hook
        method to execute any custom validation steps.
        """
        draft_id = self._get_draft_id()

        self.parent.logger.info(f"Validating publish for draft id: {draft_id}")

        if not draft_id:
            message = "No draft associated with the current context. Please make sure you have a draft opened."
            self.parent.logger.error(message)
            QtGui.QMessageBox.critical(
                None,
                "Error",
                message,
            )
            return False

        return True
