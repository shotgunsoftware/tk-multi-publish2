# Copyright (c) 2023 Autodesk
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk.

import os
import pprint
import traceback

import sgtk
from sgtk import TankError
from sgtk.util.filesystem import copy_file, ensure_folder_exists


HookBaseClass = sgtk.get_hook_baseclass()


# import sys
# sys.path.append("C:\\python_libs")
# import ptvsd
# ptvsd.enable_attach()
# ptvsd.wait_for_attach()


class MaterialTexturePublishPlugin(HookBaseClass):
    """Plugin for creating Material publishes in ShotGrid."""

    ############################################################################
    # standard publish plugin properties

    @property
    def icon(self):
        """Path to an png icon on disk."""

        return os.path.join(self.disk_location, "icons", "publish.png")

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """
        Publishes the file to a Material entity in ShotGrid. A <b>Publish</b>
        entry will be created in ShotGrid and linked to the selected Material.
        """

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

        base_settings = super(MaterialTexturePublishPlugin, self).settings

        plugin_settings = {
            "Publish Template": {
                "type": "str",
                "default": None,
                "description": "Location to copy texture files on publish."
            },
        }

        base_settings.update(plugin_settings)
        return base_settings

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """

        return [
            "material.texture",
        ]

    ############################################################################
    # standard publish plugin methods

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

        path = item.get_property("path")
        if path is None:
            raise AttributeError("'PublishData' object has no attribute 'path'")
        
        material_path = item.get_property("material_path")
        if material_path is None:
            raise AttributeError("'PublishData' object has no attribute 'material_path'")
        
        self.logger.info(
            "File publisher plugin accepted: %s" % (path,),
            extra={"action_show_folder": {"path": path, "material_path": material_path}},
        )

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

        return super(MaterialTexturePublishPlugin, self).validate(settings, item)

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        publisher = self.parent

        # First, copy the local file to the publish template path
        self._copy_to_publish_template(settings, item)

        publish_dependencies_ids = []
        if "sg_publish_data" in item.parent.properties:
            publish_dependencies_ids.append(
                item.parent.properties.sg_publish_data["id"]
            )

        # Publish the texture to ShotGrid

        # NOTE set as Texture Image?
        publish_type = self.get_publish_type(settings, item)

        publish_name = self.get_publish_name(settings, item)
        publish_version_number = self.get_publish_version_number(settings, item)
        publish_path = self.get_publish_path(settings, item)
        publish_user = self.get_publish_user(settings, item)
        publish_fields = self.get_publish_fields(settings, item)
        publish_kwargs = self.get_publish_kwargs(settings, item)
        publish_dependencies_paths = self.get_publish_dependencies(settings, item)
        publish_data = {
            "tk": publisher.sgtk,
            "context": item.context,
            "comment": item.description,
            "path": publish_path,
            "name": publish_name,
            "created_by": publish_user,
            "version_number": publish_version_number,
            "thumbnail_path": item.get_thumbnail_as_path(),
            "published_file_type": publish_type,
            "dependency_paths": publish_dependencies_paths,
            "dependency_ids": publish_dependencies_ids,
            "sg_fields": publish_fields,
        }
        publish_data.update(publish_kwargs)
        self.logger.debug(
            "Populated Publish data...",
            extra={
                "action_show_more_info": {
                    "label": "Publish Data",
                    "tooltip": "Show the complete Publish data dictionary",
                    "text": "<pre>%s</pre>" % (pprint.pformat(publish_data),),
                }
            },
        )
        # Create the publish and stash it in the item properties for other plugins to use.
        item.properties.sg_publish_data = sgtk.util.register_publish(**publish_data)
        self.logger.info("Publish registered!")
        self.logger.debug(
            "ShotGrid Publish data...",
            extra={
                "action_show_more_info": {
                    "label": "ShotGrid Publish Data",
                    "tooltip": "Show the complete ShotGrid Publish Entity dictionary",
                    "text": "<pre>%s</pre>"
                    % (pprint.pformat(item.properties.sg_publish_data),),
                }
            },
        )


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

        super(MaterialTexturePublishPlugin, self).finalize(settings, item)

    ############################################################################
    # Helper methods
    #

    def get_publish_template(self, settings, item):
        """
        Get a publish template for the supplied settings and item.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish template for

        :return: A template representing the publish path of the item or
            None if no template could be identified.
        """

        publish_template_setting = settings.get("Publish Template")

        if publish_template_setting:
            publish_template = self.parent.engine.get_template_by_name(
                publish_template_setting.value
            )
            if publish_template:
                return publish_template

        return item.get_property("publish_template")

    def get_publish_path(self, settings, item):
        """
        Get a publish path for the supplied settings and item.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish path for

        :return: A string representing the output path to supply when
            registering a publish for the supplied item

        Extracts the publish path via the configured work and publish templates
        if possible.
        """

        restore_path = item.get_property("path")
        material_path = item.get_property("material_path")
        item.properties["path"] = material_path
        try:
            material_publish_path = super(MaterialTexturePublishPlugin, self).get_publish_path(settings, item)
        finally:
            item.properties["path"] = restore_path

        texture_path = item.get_property("path")
        texture_file = os.path.basename(texture_path)
        return os.path.join(material_publish_path, texture_file)

    def get_publish_name(self, settings, item):
        """
        Get the publish name for the supplied settings and item.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish name for

        Uses the path info hook to retrieve the publish name.
        """

        # publish name explicitly set or defined on the item
        publish_name = item.get_property("publish_name")
        if publish_name:
            return publish_name

        # fall back to the path_info logic
        publisher = self.parent
        path = item.get_property("path")
        if path is None:
            raise AttributeError("'PublishData' object has no attribute 'path'")

        return publisher.util.get_publish_name(path, sequence=False)

    ############################################################################
    # protected methods
