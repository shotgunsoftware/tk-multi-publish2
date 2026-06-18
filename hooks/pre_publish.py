# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtGui

HookBaseClass = sgtk.get_hook_baseclass()


class PrePublishHook(HookBaseClass):
    """
    This hook defines logic to be executed before showing the publish
    dialog. There may be conditions that need to be checked before allowing
    the user to proceed to publishing.
    """

    def validate(self):
        """
        Returns True if the user can proceed to publish. Override this hook
        method to execute any custom validation steps.
        """
        app = self.parent

        # -- Flow AM: DCC engine require an open draft before showing the publish dialog
        if self._flowam_active_for_dcc():
            if not self._flow_validate(app):
                return False
        return True

    ############################################################################
    # Flow AM helpers

    def _flow_validate(self, app):
        """
        Flow AM branch for ``validate``.

        Ensures a draft is open in the DCC before the publish dialog is shown.
        Returns False (with a dialog) if no draft is associated with the context.
        """
        flow_draft_id = self.parent.context.flow_draft_id
        app.logger.info(f"Validating publish for draft id: {flow_draft_id}")

        if not flow_draft_id:
            message = (
                "No draft associated with the current context. "
                "Please make sure you have a draft opened."
            )
            app.logger.error(message)
            QtGui.QMessageBox.critical(None, "Error", message)
            return False
        return True

    def _flowam_active_for_dcc(self):
        """Return True only when current engine is DCC AND the app
        context is a Flow project."""
        if self.parent.context.flow_project_id is None:
            return False
        engine = sgtk.platform.current_engine()
        return engine is not None and engine.name != "tk-desktop"
