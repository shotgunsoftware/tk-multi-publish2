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
import pprint

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class DccFlowPublishPlugin(HookBaseClass):
    """
    Self-contained DCC publish plugin for Flow Asset Management integration.

    Subclasses ``publish_file.py`` directly via the hook chain::

        hook: "{self}/publish_file.py:{self}/flowam/publish_to_flow.py:{engine}/tk-multi-publish2/basic/publish_session.py"

    Handles the full DCC publish workflow: framework loading, project
    validation, draft validation, conflict checking, and publishing via
    ``publish_dcc_draft`` in the Flow AM SDK.

    The desktop counterpart lives in
    ``tk-desktop/hooks/tk-multi-publish2/flowam/publish_to_flow.py``
    (``DesktopFlowPublishPlugin``). Shared logic (properties, ``publish``,
    ``finalize``, ``get_publish_user``) is duplicated between the two so
    each plugin can evolve independently across separate release cycles.
    When updating shared logic, apply the change to both files.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the plugin."""
        super().__init__(*args, **kwargs)
        self.draft_id = None
        self.flow_module = None
        self.sg_flow_am_id = None

    ############################################################################
    # standard publish plugin properties

    @property
    def icon(self):
        return os.path.join(self.disk_location, "icons", "flow.png")

    @property
    def name(self):
        return "Publish to Flow AM"

    @property
    def description(self):
        return """
        Publishes the file to Flow Production Tracking and Asset Manager. A <b>Publish</b> entry
        will be created in Flow Production Tracking which will include a reference
        to the file's current path on disk. Other users will be able to access the
        published file via the <b><a href='%s'>Loader</a></b> so long as they have
        access to the file's location on disk.

        <h3>Overwriting an existing publish</h3>
        A file can be published multiple times however only the most recent
        publish will be available to other users. Warnings will be provided
        during validation if there are previous publishes.
        """

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """
        return ["file.*"]

    ############################################################################
    # standard publish plugin methods

    def accept(self, settings, item):
        """
        Method called by the publisher to determine if an item is of any
        interest to this plugin. Only items matching the filters defined via the
        item_filters property will be presented to this method.
        """
        path = item.get_property("path")
        if path is None:
            raise AttributeError("'PublishData' object has no attribute 'path'")

        # log the accepted file and display a button to reveal it in the fs
        self.logger.info(
            "File publisher plugin accepted: %s" % (path,),
            extra={"action_show_folder": {"path": path}},
        )

        return {"accepted": True}

    def validate(self, settings, item):
        """
        Validates project configuration, AM project ID, open draft, and asset
        conflicts. Combines base project validation with DCC-specific draft
        validation - no super() call needed.
        """
        # FlowAM framework import
        # TODO: We have an issue on FPTR desktop where the `adsk` cannot be found
        flow_am_fw = self.load_framework("tk-framework-flowam_v1.x.x")
        self.flow_module = flow_am_fw.import_module("flow")

        publisher = self.parent

        # Get the project's sg_flow_am_id
        sg_flow_project_id = sgtk.platform.current_engine().context.project["id"]
        project = publisher.shotgun.find_one(
            "Project", [["id", "is", sg_flow_project_id]], ["sg_flow_am_id"]
        )
        self.sg_flow_am_id = project.get("sg_flow_am_id")
        if not self.sg_flow_am_id:
            self.logger.error(
                "Project {} has no sg_flow_am_id set. "
                "Please set the sg_flow_am_id field on the project.".format(
                    project["name"]
                )
            )
            return False

        self.logger.info("Validating AM Project ID")
        am = self.flow_module.asset_management
        project_valid, project_err = am.validate_project(self.sg_flow_am_id)
        if not project_valid:
            self.logger.error(
                f"No Flow project associated with current SG project: {project_err}"
            )
            return False

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

    def publish(self, settings, item):
        """Publish the item to Flow AM."""
        try:
            pub_info = self._publish_to_flow(item)

            # Check if user cancelled (child process return None)
            if pub_info is None:
                raise self.parent.base_hooks.PublishCancelledException(
                    "User cancelled the publish to Flow AM."
                )
            self.logger.info("Publish to Flow AM successful")

            # Store publish info for downstream plugins (e.g., alembic derivative)
            item.properties["am_publish_info"] = pub_info
            item.properties["entity"] = item.context.entity or item.context.project
            item.properties["task"] = item.context.task

            self.logger.info("Publish registered!")
            self.logger.debug(
                "Flow AM Publish info...",
                extra={
                    "action_show_more_info": {
                        "label": "Flow AM Publish Info",
                        "tooltip": "Show the complete Flow AM Publish info",
                        "text": "<pre>%s</pre>" % (pprint.pformat(pub_info.__dict__),),
                    }
                },
            )
        except self.parent.base_hooks.PublishCancelledException:
            # Re-raise cancellation exception without logging as error
            # The dialog will handle this and show "Publish Cancelled"
            raise
        except Exception as e:
            self.logger.error(
                "Failed to publish to Flow AM",
                extra={
                    "action_show_more_info": {
                        "label": "Error Details",
                        "text": "<pre>" f"{e}\n" "</pre>",
                    }
                },
            )
            raise

    def finalize(self, settings, item):
        pass

    def get_publish_user(self, settings, item):
        """
        Get the user that will be associated with this publish.

        If publish_user is not defined as a ``property`` or ``local_property``,
        this method will return ``None``.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish template for

        :return: A user entity dictionary or ``None`` if not defined.
        """
        return item.context.user

    ############################################################################
    # protected methods

    def _publish_to_flow(self, item):
        """
        Performs the DCC publish by calling ``publish_dcc_draft`` in the Flow
        AM SDK. Uses ``self.draft_id`` set during ``validate()``.
        """
        flow_args = dict(
            comment=item.description or "",
            thumbnail_path=item.get_thumbnail_as_path(),
        )
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

        return pub_info
