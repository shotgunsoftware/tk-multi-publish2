# Copyright (c) 2025 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import pprint

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class FlowDccPublishPlugin(HookBaseClass):
    """
    Publish plugin for Flow AM integration.

    This publish plugin class should inherit from `publish_to_flow.FlowPublishPlugin`.

    It extends the base functionality to include Flow AM specific logic for
    validating the context, publishing items, and updating publish proxies when executing
    on a DCC like Maya or Houdini.
    """

    def validate(self, settings, item):
        """
        DCC-specific validation that includes draft validation.
        Requires a draft to be opened in the DCC context.
        """
        if not super().validate(settings, item):
            return False

        # Uses self.flow_module set by parent class and get draft_id from the asset manager context
        am = self.flow_module.asset_management
        self.draft_id = am.FlowContext.draft_id

        # DCC publishing requires a draft to be opened
        if not self.draft_id:
            self.logger.error(
                "No draft associated with the current context. Please make sure you have a draft opened."
            )
            return False

        self.logger.debug(f"Using AM draft_id: {self.draft_id}")

        # Ensure parent has no other children of the same dcc workfile type
        has_conflict, conflict_err = am.has_asset_conflict(self.draft_id)
        if has_conflict:
            self.logger.error(f"Asset conflict detected: {conflict_err}")
            return False

        return True

    def _publish_to_flow(self, settings, item):
        # Step 1: Prepare. Add the Flow AM specific data
        flow_args = self._get_flow_args(item)
        flow_args["am_draft_id"] = self.draft_id
        publish_inputs = self.flow_module.asset_management.PublishInputs(**flow_args)

        self.logger.debug(
            "Data for FlowAM is ready:",
            extra={
                "action_show_more_info": {
                    "label": "See contents",
                    "text": "<pre>" f"{pprint.pformat(flow_args)}\n" "</pre>",
                }
            },
        )

        # Step 2: Publish the draft on the framework
        # Note: No try-except here. If this fails, the exception propagates to the
        # parent publish() method which handles error logging.
        pub_info = self.flow_module.asset_management.publish_dcc_draft(publish_inputs)

        # Return pub_info framework data for later use
        return pub_info
