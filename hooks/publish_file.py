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
import pprint
import traceback

import sgtk
from sgtk.util.filesystem import copy_file, ensure_folder_exists

HookBaseClass = sgtk.get_hook_baseclass()


class BasicFilePublishPlugin(HookBaseClass):
    """
    Plugin for creating generic publishes in Shotgun.

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
            "publish.png"
        )

    @property
    def name(self):
        """
        One line display name describing the plugin
        """
        return "Publish to Shotgun"

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        loader_url = "https://support.shotgunsoftware.com/hc/en-us/articles/219033078"

        return """
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
                    ["Alembic Cache", "abc"],
                    ["3dsmax Scene", "max"],
                    ["NukeStudio Project", "hrox"],
                    ["Houdini Scene", "hip", "hipnc"],
                    ["Maya Scene", "ma", "mb"],
                    ["Nuke Script", "nk"],
                    ["Photoshop Image", "psd", "psb"],
                    ["Rendered Image", "dpx", "exr"],
                    ["Texture", "tiff", "tx", "tga", "dds"],
                    ["Image", "jpeg", "jpg", "png"],
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
        return ["file.*"]

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
            "File publisher plugin accepted: %s" % (path,),
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
        Validates the given item to check that it is ok to publish.

        Returns a boolean to indicate validity.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process

        :returns: True if item is valid, False otherwise.
        """

        publisher = self.parent
        path = item.properties.get("path")

        # ---- determine the information required to validate

        # We allow the information to be pre-populated by the collector or a
        # base class plugin. They may have more information than is available
        # here such as custom type or template settings.

        publish_path = item.properties.get("publish_path") or \
            self._get_publish_path(settings, item)

        publish_name = item.properties.get("publish_name") or \
            self._get_publish_name(settings, item)

        # ---- check for conflicting publishes of this path with a status

        # Note the name, context, and path *must* match the values supplied to
        # register_publish in the publish phase in order for this to return an
        # accurate list of previous publishes of this file.
        publishes = publisher.util.get_conflicting_publishes(
            item.context,
            publish_path,
            publish_name,
            filters=["sg_status_list", "is_not", None]
        )

        if publishes:
            conflict_info = (
                "If you continue, these conflicting publishes will no longer "
                "be available to other users via the loader:<br>"
                "<pre>%s</pre>" % (pprint.pformat(publishes),)
            )
            self.logger.warn(
                "Found %s conflicting publishes in Shotgun" %
                    (len(publishes),),
                extra={
                    "action_show_more_info": {
                        "label": "Show Conflicts",
                        "tooltip": "Show the conflicting publishes in Shotgun",
                        "text": conflict_info
                    }
                }
            )

        self.logger.info("A Publish will be created in Shotgun and linked to:")
        self.logger.info("  %s" % (path,))

        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        publisher = self.parent

        # ---- determine the information required to publish

        # We allow the information to be pre-populated by the collector or a
        # base class plugin. They may have more information than is available
        # here such as custom type or template settings.

        publish_type = item.properties.get("publish_type") or \
            self._get_publish_type(settings, item)

        publish_name = item.properties.get("publish_name") or \
            self._get_publish_name(settings, item)

        publish_version = item.properties.get("publish_version") or \
            self._get_publish_version(settings, item)

        publish_path = item.properties.get("publish_path") or \
            self._get_publish_path(settings, item)

        # if the parent item has a publish path, include it in the list of
        # dependencies
        dependency_paths = item.properties.get("publish_dependencies", [])
        if "sg_publish_path" in item.parent.properties:
            dependency_paths.append(item.parent.properties["sg_publish_path"])

        # handle copying of work to publish if templates are in play
        self._copy_work_to_publish(settings, item)

        # arguments for publish registration
        self.logger.info("Registering publish...")
        publish_data= {
            "tk": publisher.sgtk,
            "context": item.context,
            "comment": item.description,
            "path": publish_path,
            "name": publish_name,
            "version_number": publish_version,
            "thumbnail_path": item.get_thumbnail_as_path(),
            "published_file_type": publish_type,
            "dependency_paths": dependency_paths
        }

        # log the publish data for debugging
        self.logger.debug(
            "Populated Publish data...",
            extra={
                "action_show_more_info": {
                    "label": "Publish Data",
                    "tooltip": "Show the complete Publish data dictionary",
                    "text": "<pre>%s</pre>" % (pprint.pformat(publish_data),)
                }
            }
        )

        # create the publish and stash it in the item properties for other
        # plugins to use.
        item.properties["sg_publish_data"] = sgtk.util.register_publish(
            **publish_data)
        self.logger.info("Publish registered!")

    def finalize(self, settings, item):
        """
        Execute the finalization pass. This pass executes once
        all the publish tasks have completed, and can for example
        be used to version up files.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        publisher = self.parent

        # get the data for the publish that was just created in SG
        publish_data = item.properties["sg_publish_data"]

        # ensure conflicting publishes have their status cleared
        publisher.util.clear_status_for_conflicting_publishes(
            item.context, publish_data)

        self.logger.info(
            "Cleared the status of all previous, conflicting publishes")

        path = item.properties["path"]
        self.logger.info(
            "Publish created for file: %s" % (path,),
            extra={
                "action_show_in_shotgun": {
                    "label": "Show Publish",
                    "tooltip": "Open the Publish in Shotgun.",
                    "entity": publish_data
                }
            }
        )

    ############################################################################
    # protected methods

    def _copy_work_to_publish(self, settings, item):
        """
        This method handles copying work file path(s) to a designated publish
        location.

        This method requires a "work_template" and a "publish_template" be set
        on the supplied item.

        The method will handle copying the "path" property to the corresponding
        publish location assuming the path corresponds to the "work_template"
        and the fields extracted from the "work_template" are sufficient to
        satisfy the "publish_template".

        The method will not attempt to copy files if any of the above
        requirements are not met. If the requirements are met, the file will
        ensure the publish path folder exists and then copy the file to that
        location.

        If the item has "sequence_paths" set, it will attempt to copy all paths
        assuming they meet the required criteria with respect to the templates.

        """

        # ---- ensure templates are available
        work_template = item.properties.get("work_template")
        if not work_template:
            self.logger.debug(
                "No work template set on the item. "
                "Skipping copy file to publish location."
            )
            return

        publish_template = item.properties.get("publish_template")
        if not publish_template:
            self.logger.debug(
                "No publish template set on the item. "
                "Skipping copying file to publish location."
            )
            return

        # ---- get a list of files to be copied

        # by default, the path that was collected for publishing
        work_files = [item.properties["path"]]

        # if this is a sequence, get the attached files
        if "sequence_paths" in item.properties:
            work_files = item.properties.get("sequence_paths", [])
            if not work_files:
                self.logger.warning(
                    "Sequence publish without a list of files. Publishing "
                    "the sequence path in place: %s" % (item.properties["path"])
                )
                return

        # ---- copy the work files to the publish location

        for work_file in work_files:

            if not work_template.validate(work_file):
                self.logger.warning(
                    "Work file '%s' did not match work template '%s'. "
                    "Publishing in place." % (work_file, work_template)
                )
                return

            work_fields = work_template.get_fields(work_file)

            missing_keys = publish_template.missing_keys(work_fields)

            if missing_keys:
                self.logger.warning(
                    "Work file '%s' missing keys required for the publish "
                    "template: %s" % (work_file, missing_keys)
                )
                return

            publish_file = publish_template.apply_fields(work_fields)

            # copy the file
            try:
                publish_folder = os.path.dirname(publish_file)
                ensure_folder_exists(publish_folder)
                copy_file(work_file, publish_file)
            except Exception, e:
                raise Exception(
                    "Failed to copy work file from '%s' to '%s'.\n%s" %
                    (work_file, publish_file, traceback.format_exc())
                )

            self.logger.debug(
                "Copied work file '%s' to publish file '%s'." %
                (work_file, publish_file)
            )

    def _get_publish_type(self, settings, item):
        """
        Get a publish type for the supplied settings and item.

        :param settings: The publish settings defining the publish types
        :param item: The item to determine the publish type for

        :return: A publish type or None if one could not be found.
        """

        publisher = self.parent
        path = item.properties["path"]

        # get the publish path components
        path_info = publisher.util.get_file_path_components(path)

        # determine the publish type
        extension = path_info["extension"]

        # ensure lowercase and no dot
        if extension:
            extension = extension.lstrip(".").lower()

            for type_def in settings["File Types"].value:

                publish_type = type_def[0]
                file_extensions = type_def[1:]

                if extension in file_extensions:
                    # found a matching type in settings. use it!
                    return publish_type

        # --- no pre-defined publish type found...

        if extension:
            # publish type is based on extension
            publish_type = "%s File" % extension.capitalize()
        else:
            # no extension, assume it is a folder
            publish_type = "Folder"

        return publish_type

    def _get_publish_path(self, settings, item):
        """
        Get a publish path for the supplied settings and item.

        :param settings: The publish settings defining the publish types
        :param item: The item to determine the publish type for

        :return: A string representing the output path to supply when
            registering a publish for the supplied item

        Extracts the publish path via the configured work and publish templates
        if possible.
        """

        path = item.properties["path"]

        work_template = item.properties.get("work_template")
        publish_template = item.properties.get("publish_template")

        work_fields = []
        publish_path = None

        # We need both work and publish template to be defined for template support to be enabled.
        if work_template and publish_template:
            if work_template.validate(path):
                work_fields = work_template.get_fields(path)

            missing_keys = publish_template.missing_keys(work_fields)

            if missing_keys:
                self.logger.warning(
                    "Not enough keys to apply work fields (%s) to "
                    "publish template (%s)" % (work_fields, publish_template))
            else:
                publish_path = publish_template.apply_fields(work_fields)
                self.logger.debug(
                    "Used publish template to determine the publish path: %s" %
                    (publish_path,)
                )
        else:
            self.logger.debug("publish_template: %s" % publish_template)
            self.logger.debug("work_template: %s" % work_template)

        if not publish_path:
            publish_path = path
            self.logger.debug(
                "Could not validate a publish template. Publishing in place.")

        return publish_path

    def _get_publish_version(self, settings, item):
        """
        Get the publish version for the supplied settings and item.

        :param settings: The publish settings defining the publish types
        :param item: The item to determine the publish version for

        Extracts the publish version via the configured work template if
        possible. Will fall back to using the path info hook.
        """

        publisher = self.parent
        path = item.properties["path"]

        work_template = item.properties.get("work_template")
        work_fields = None
        publish_version = None

        if work_template:
            if work_template.validate(path):
                self.logger.debug(
                    "Work file template configured and matches file.")
                work_fields = work_template.get_fields(path)

        if work_fields:
            # if version number is one of the fields, use it to populate the
            # publish information
            if "version" in work_fields:
                publish_version = work_fields.get("version")
                self.logger.debug(
                    "Retrieved version number via work file template.")

        else:
            self.logger.debug("Using path info hook to determine publish version.")
            publish_version = publisher.util.get_version_number(path)
            if publish_version is None:
                publish_version = 1

        return publish_version

    def _get_publish_name(self, settings, item):
        """
        Get the publish name for the supplied settings and item.

        :param settings: The publish settings defining the publish types
        :param item: The item to determine the publish version for

        Uses the path info hook to retrieve the publish name.
        """

        publisher = self.parent
        path = item.properties["path"]

        if "sequence_paths" in item.properties:
            # generate the name from one of the actual files in the sequence
            name_path = item.properties["sequence_paths"][0]
            is_sequence = True
        else:
            name_path = path
            is_sequence = False

        return publisher.util.get_publish_name(
            name_path,
            sequence=is_sequence
        )

    def _get_next_version_info(self, path, item):
        """
        Return the next version of the supplied path.

        If templates are configured, use template logic. Otherwise, fall back to
        the zero configuration, path_info hook logic.

        :param str path: A path with a version number.
        :param item: The current item being published

        :return: A tuple of the form::

            # the first item is the supplied path with the version bumped by 1
            # the second item is the new version number
            (next_version_path, version)
        """

        if not path:
            self.logger.debug("Path is None. Can not determine version info.")
            return None, None

        publisher = self.parent

        # if the item has a known work file template, see if the path
        # matches. if not, warn the user and provide a way to save the file to
        # a different path
        work_template = item.properties.get("work_template")
        work_fields = None

        if work_template:
            if work_template.validate(path):
                work_fields = work_template.get_fields(path)

        # if we have template and fields, use them to determine the version info
        if work_fields and "version" in work_fields:

            # template matched. bump version number and re-apply to the template
            work_fields["version"] += 1
            next_version_path = work_template.apply_fields(work_fields)
            version = work_fields["version"]

        # fall back to the "zero config" logic
        else:
            next_version_path = publisher.util.get_next_version_path(path)
            cur_version = publisher.util.get_version_number(path)
            if cur_version is not None:
                version = cur_version + 1
            else:
                version = None

        return next_version_path, version

    def _save_to_next_version(self, path, item, save_callback):
        """
        Save the supplied path to the next version on disk.

        :param path: The current path with a version number
        :param item: The current item being published
        :param save_callback: A callback to use to save the file

        Relies on the _get_next_version_info() method to retrieve the next
        available version on disk. If a version can not be detected in the path,
        the method does nothing.

        If the next version path already exists, logs a warning and does
        nothing.

        This method is typically used by subclasses that bump the current
        working/session file after publishing.
        """

        (next_version_path, version) = self._get_next_version_info(path, item)

        if version is None:
            self.logger.debug(
                "No version number detected in the publish path. "
                "Skipping the bump file version step."
            )
            return None

        self.logger.info("Incrementing file version number...")

        # nothing to do if the next version path can't be determined or if it
        # already exists.
        if not next_version_path:
            self.logger.warning("Could not determine the next version path.")
            return None
        elif os.path.exists(next_version_path):
            self.logger.warning(
                "The next version of the path already exists",
                extra={
                    "action_show_folder": {
                        "path": next_version_path
                    }
                }
            )
            return None

        # save the file to the new path
        save_callback(next_version_path)
        self.logger.info("File saved as: %s" % (next_version_path,))

        return next_version_path
