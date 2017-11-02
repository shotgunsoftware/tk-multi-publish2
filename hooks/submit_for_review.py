# Copyright (c) 2017 Shotgun Software Inc.
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


HookBaseClass = sgtk.get_hook_baseclass()


class BasicSubmitForReviewPlugin(HookBaseClass):
    """
    TODO: UPDATE TO SUBMIT FOR REVIEW!!!!!!

    Plugin for submitting a review in Shotgun.

    This plugin is typically configured to act upon files that are dragged and
    dropped into the publisher UI. It can also be used as a base class for
    other file-based publish plugins as it contains standard operations for
    validating and registering publishes with Shotgun.

    Once attached to a publish item, the plugin will key off of properties that
    are set on the item. These properties can be set via the collector or
    by subclasses prior to calling methods on this class.

    The only property that is required for the plugin to operate is the ``path``
    property. All of the properties understood by the plugin are documented
    below::

        Path properties
        -------------

        path - The path to the file to be published.

        sequence_paths - If set, implies the "path" property represents a
            sequence of files (typically using a frame identifier such as %04d).
            This property should be a list of files on disk matching the "path".
            If a work template is provided, and corresponds to the listed
            frames, fields will be extracted and applied to the publish template
            (if set) and copied to that publish location.

        Template properties
        -------------------

        work_template - If set in the item properties dictionary, is used
            to validate "path" and extract fields for further processing and
            contextual discovery. For example, if configured and a version key
            can be extracted, it will be used as the publish version to be
            registered in Shotgun.

        published_template - If set in the item properties dictionary, used to
            determine where "path" should be copied prior to publishing. If
            not specified, "path" will be published in place.

        Publish properties
        ------------------

        publish_type - If set in the item properties dictionary, will be
            supplied to SG as the publish type when registering "path" as a new
            publish. If not set, will be determined via the plugin's "File Type"
            setting.

        publish_path - If set in the item properties dictionary, will be
            supplied to SG as the publish path when registering the new publish.
            If not set, will be determined by the "published_file" property if
            available, falling back to publishing "path" in place.

        publish_name - If set in the item properties dictionary, will be
            supplied to SG as the publish name when registering the new publish.
            If not available, will be determined by the "work_template"
            property if available, falling back to the ``path_info`` hook
            logic.

        publish_version - If set in the item properties dictionary, will be
            supplied to SG as the publish version when registering the new
            publish. If not available, will be determined by the
            "work_template" property if available, falling back to the
            ``path_info`` hook logic.

        publish_dependencies - A list of files to include as dependencies when
            registering the publish. If the item's parent has been published,
            it's path will be appended to this list.

    This plugin will also set the properties on the item which may be useful for
    child items.

        sg_publish_data - The dictionary of publish information returned from
            the tk-core register_publish method.

    """

    @property
    def icon(self):
        """
        Path to an png icon on disk
        """

        # look for icon one level up from this hook's folder in "icons" folder
        return os.path.join(
            self.disk_location,
            "icons",
            "review.png"
        )

    @property
    def name(self):
        """
        One line display name describing the plugin
        """
        return "Submit for Review"

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        loader_url = "https://support.shotgunsoftware.com/hc/en-us/articles/219033078"

        return """
        TODO: UPDATE TO SUBMIT FOR REVIEW!!!!!!

        Publishes the file to Shotgun. A <b>Publish</b> entry will be
        created in Shotgun which will include a reference to the file's current
        path on disk. Other users will be able to access the published file via
        the <b><a href='%s'>Loader</a></b> so long as they have access to
        the file's location on disk.

        <h3>File versioning</h3>
        The <code>version</code> field of the resulting <b>Publish</b> in
        Shotgun will also reflect the version number identified in the filename.
        The basic worklfow recognizes the following version formats by default:

        <ul>
        <li><code>filename.v###.ext</code></li>
        <li><code>filename_v###.ext</code></li>
        <li><code>filename-v###.ext</code></li>
        </ul>

        <br><br><i>NOTE: any amount of version number padding is supported.</i>

        <h3>Overwriting an existing publish</h3>
        A file can be published multiple times however only the most recent
        publish will be available to other users. Warnings will be provided
        during validation if there are previous publishes.
        """ % (loader_url,)

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to recieve
        through the settings parameter in the accept, validate, publish and
        finalize methods.

        A dictionary on the following form::

            {
                "Settings Name": {
                    "type": "settings_type",
                    "default": "default_value",
                    "description": "One line description of the setting"
            }

        The type string should be one of the data types that toolkit accepts
        as part of its environment configuration.
        """
        return {
            "File Types": {
                "type": "list",
                "default": [
                    ["Movie", "mov", "mp4"],
                ],
                "description": (
                    "List of file types to include. Each entry in the list "
                    "is a list in which the first entry is the Shotgun "
                    "published file type and subsequent entries are file "
                    "extensions that should be associated."
                )
            },
        }

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """
        return ["*.sequence"]

    def accept(self, settings, item):
        """
        Method called by the publisher to determine if an item is of any
        interest to this plugin. Only items matching the filters defined via the
        item_filters property will be presented to this method.

        A publish task will be generated for each item accepted here. Returns a
        dictionary with the following booleans:

            - accepted: Indicates if the plugin is interested in this value at
                all. Required.
            - enabled: If True, the plugin will be enabled in the UI, otherwise
                it will be disabled. Optional, True by default.
            - visible: If True, the plugin will be visible in the UI, otherwise
                it will be hidden. Optional, True by default.
            - checked: If True, the plugin will be checked in the UI, otherwise
                it will be unchecked. Optional, True by default.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process

        :returns: dictionary with boolean keys accepted, required and enabled
        """

        path = item.properties["path"]

        # log the accepted file and display a button to reveal it in the fs
        self.logger.info(
            "Submit for review plugin accepted: %s" % (path,),
            extra={
                "action_show_folder": {
                    "path": path
                }
            }
        )

        # return the accepted info
        return {"accepted": True}

    def validate(self, settings, item):
        """
        Validates the given item to check that it is ok to publish. Returns a
        boolean to indicate validity.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        :returns: True if item is valid, False otherwise.
        """

        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        sg_publish = item.properties["sg_publish_data"]
        sg_task = self.parent.context.task
        comment = item.description
        thumbnail_path = item.get_thumbnail_as_path()
        progress_cb = lambda *args, **kwargs: None
        review_submission_app = self.parent.engine.apps.get("tk-multi-reviewsubmission")

        render_path = item.properties.get("path")
        render_template = item.properties.get("work_template")
        publish_template = item.properties.get("publish_template")
        render_path_fields = render_template.get_fields(render_path)
        first_frame = item.properties.get("first_frame")
        last_frame = item.properties.get("last_frame")

        if hasattr(review_submission_app, "render_and_submit_version"):
            # this is a recent version of the review submission app that contains
            # the new method that also accepts a colorspace argument.
            colorspace = item.properties.get("color_space")
            review_submission_app.render_and_submit_version(
                publish_template,
                render_path_fields,
                first_frame,
                last_frame,
                [sg_publish],
                sg_task,
                comment,
                thumbnail_path,
                progress_cb,
                colorspace
            )
        else:
            # This is an older version of the app so fall back to the legacy
            # method - this may mean the colorspace of the rendered movie is
            # inconsistent/wrong!
            review_submission_app.render_and_submit(
                publish_template,
                render_path_fields,
                first_frame,
                last_frame,
                [sg_publish],
                sg_task,
                comment,
                thumbnail_path,
                progress_cb
            )

    def finalize(self, settings, item):
        """
        Execute the finalization pass. This pass executes once all the publish
        tasks have completed, and can for example be used to version up files.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """
        pass
