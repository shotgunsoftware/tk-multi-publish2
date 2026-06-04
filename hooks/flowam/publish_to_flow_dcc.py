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


class DccFlowPublishPlugin(HookBaseClass):
    """
    DCC publish plugin for Flow Asset Management.

    Sits on top of ``FlowPublishPlugin`` in the hook chain::

        hook: "{self}/publish_file.py:{self}/flowam/publish_to_flow.py:{self}/flowam/publish_to_flow_dcc.py:{engine}/tk-multi-publish2/basic/publish_session.py"

    Adds DCC-specific validation (open draft + asset conflict check) and
    performs the publish via ``publish_dcc_draft`` in the Flow AM SDK.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.draft_id = None

    def validate(self, settings, item):
        """
        Run the base project validation, then check that an AM draft is open
        and that there is no asset conflict for that draft.
        """
        if not super().validate(settings, item):
            return False

        am = self.flow_module.asset_management

        # DCC publishing requires a draft to be opened
        self.draft_id = am.FlowContext.draft_id
        if not self.draft_id:
            self.logger.error(
                "No draft associated with the current context. "
                "Please make sure you have a draft opened."
            )
            return False

        self.logger.debug(f"Using AM draft_id: {self.draft_id}")

        # Ensure parent has no other children of the same dcc workfile type
        has_conflict, conflict_err = am.has_asset_conflict(self.draft_id)
        if has_conflict:
            self.logger.error(f"Asset conflict detected: {conflict_err}")
            return False

        return True

    def _publish_to_flow(self, item):
        """
        Perform the DCC publish by calling ``publish_dcc_draft`` in the Flow
        AM SDK. Uses ``self.draft_id`` set during ``validate()``.
        """
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

        # Note: No try-except here. If this fails, the exception propagates to
        # publish() which handles error logging.
        pub_info = self.flow_module.asset_management.publish_dcc_draft(publish_inputs)

        # Return pub_info framework data for later use
        return pub_info
