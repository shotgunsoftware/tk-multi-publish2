# Copyright (c) 2025 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

import sgtk
from tank_vendor.flow_integration_sdk.exceptions import FlowError
from tank_vendor.flow_integration_sdk.objects import FlowAsset
from tank_vendor.flow_integration_sdk.schema import get_schema_id
from tank_vendor.flow_integration_sdk.storage import storage_key_to_asset_id

HookBaseClass = sgtk.get_hook_baseclass()


class FlowPublishAlembicDerivativePlugin(HookBaseClass):
    """
    Publish plugin that registers an Alembic derivative against the
    Flow AM revision created by the main publish plugin earlier in the
    chain.

    Originally derived from ``hooks/publish_file.py`` and adapted to
    call ``flow_module.asset_management.generate_derivative`` instead
    of creating an FPT ``PublishedFile`` entity.
    """

    PUBLISH_TYPE = "Alembic"

    ############################################################################
    # standard publish plugin properties

    @property
    def icon(self):
        """
        Path to an png icon on disk
        """

        # look for icon one level up from this hook's folder in "icons" folder
        return os.path.join(self.disk_location, "..", "icons", "alembic.png")

    @property
    def name(self):
        return "Publish Alembic Derivative"

    @property
    def description(self):
        return """
        Publish an Alembic derivative file to Flow.
        """

    ############################################################################
    # standard publish plugin methods

    def accept(self, settings, item):
        """
        Method called by the publisher to determine if an item is of any
        interest to this plugin. Only items matching the filters defined via the
        item_filters property will be presented to this method.
        """
        # if a publish template is configured, disable context change. This
        # is a temporary measure until the publisher handles context switching
        # natively.
        if settings.get("Publish Template").value:
            item.context_change_allowed = False

        draft_id = item.context.flow_draft_id

        # Check if this is a template asset via AM type system
        accepted = True
        if draft_id:
            try:
                asset_id = storage_key_to_asset_id(draft_id)
                asset = FlowAsset(asset_id)
                template_type_id = get_schema_id("type.template")
                # Templates have template_type_id in their type_ids
                if template_type_id in asset.type_ids:
                    accepted = False  # Skip derivatives for templates
            except FlowError as e:
                self.logger.debug(
                    f"This draft template has not been published yet. {e}"
                )
                accepted = False

        return {"accepted": accepted}

    def validate(self, settings, item):
        """
        Nothing to validate. We'll just generate the derivative during publish.
        """
        return True

    def publish(self, settings, item):
        # Get source revision from the main publish plugin's result
        pub_info = item.properties.get("am_publish_info")
        if not pub_info:
            self.logger.debug(
                f"Available item.properties keys: {list(item.properties.keys())}"
            )
            raise Exception(
                "No publish info found from main publish plugin. "
                "Ensure the main publish plugin ran successfully before this plugin."
            )

        try:
            inputs = self.parent.flowam.CreateDerivativeInputs(
                source_revision_id=pub_info.revision_id,
                derivative_type=self.parent.flowam.constants.DerivativeType.ALEMBIC,
                description=item.description,
                thumbnail_path=item.get_thumbnail_as_path(),
            )
            self.parent.flowam.generate_derivative(inputs)
            self.logger.info("Generate derivative in Flow AM successful")
        except Exception as e:
            self.logger.error(
                "Failed to generate Alembic derivative",
                extra={
                    "action_show_more_info": {
                        "label": "Error Details",
                        "text": f"<pre>{e}</pre>",
                    }
                },
            )
            raise

    def finalize(self, settings, item):
        """
        No-op override. Flow AM derivatives go through the Flow AM SDK,
        not the FPT PublishedFile API, so the inherited
        ``publish_file.py.finalize`` (which reads
        ``item.properties.sg_publish_data``) must be suppressed.
        """
        pass
