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


class FlowPublishPlugin(HookBaseClass):
    """
    Base publish plugin for Flow Asset Management integration.

    Originally derived from ``hooks/publish_file.py`` and adapted to
    call the Flow AM SDK instead of creating an FPT ``PublishedFile`` entity.
    Child classes (DCC, desktop) implement ``_publish_to_flow`` for their
    specific publish workflows.
    """

    DRAFT_VERSION_IDENTIFIER = -1

    def __init__(self, *args, **kwargs):
        """Initialize the plugin."""
        super().__init__(*args, **kwargs)
        # Initialize attributes used by child classes
        self.draft_id = None
        self.flow_module = None

    ############################################################################
    # standard publish plugin properties

    @property
    def icon(self):
        """
        Path to an png icon on disk
        """

        # look for icon one level up from this hook's folder in "icons" folder
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
        Common validation for all Flow AM publish plugins.
        Validates project configuration and AM project ID.
        Child classes should override this to add specific validations (e.g., draft validation for DCC).
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

        # We need to validate the project ID against the collection ID we added on initialisation
        self.logger.info("Validating AM Project ID")
        am = self.flow_module.asset_management
        project_valid, project_err = am.validate_project(self.sg_flow_am_id)

        # If the project is not valid, we cannot proceed
        if not project_valid:
            self.logger.error(
                f"No Flow project associated with current SG project: {project_err}"
            )
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
        Publish the given item to the Flow AM platform.
        To be implemented in a child class (DCC, desktop, etc)
        """
        pass

    def _get_flow_args(self, item) -> dict:
        sg_flow_thumbnail_path = item.get_thumbnail_as_path()
        return dict(
            thumbnail_path=sg_flow_thumbnail_path,
            comment=item.description or "",
        )
