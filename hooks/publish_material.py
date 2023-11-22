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


class MaterialPublishPlugin(HookBaseClass):
    """Plugin for creating Material publishes in ShotGrid."""

    @staticmethod
    def is_material(entity):
        """Return True if the entity is a Material Entity."""

        if not entity:
            return False
        # FIXME hard coded Material entity type
        return entity.get("type") in ("CustomNonProjectEntity01")

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
        return {
            "File Types": {
                "type": "list",
                "default": [
                    ["Axf File", "axf"],
                    ["VRED Material", "osb"],
                ],
                "description": (
                    "List of file types to include. Each entry in the list "
                    "is a list in which the first entry is the ShotGrid "
                    "published file type and subsequent entries are file "
                    "extensions that should be associated."
                ),
            },
            "Publish Material Template": {
                "type": "str",
                "default": None,
                "description": "Location to copy Material files on publish."
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

        return [
            "material",
            "file.vred",
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
        
        self.logger.info(
            "File publisher plugin accepted: %s" % (path,),
            extra={"action_show_folder": {"path": path}},
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

        success = True

        # TODO add option to create material on publish

        # Ensure that the entity is a Material
        if not self.is_material(item.context.entity):
            error_msg = "Entity Link must be set to a Material entity"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        # Ensure the publish path can be generated and does not overwrite an existing file
        publish_path = self.get_publish_path(settings, item)
        if not publish_path:
            error_msg = "Failed to generate publish path"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        if os.path.exists(publish_path):
            warning_msg = f"Publish will overwrite existing file {publish_path}."
            self.logger.warning(warning_msg)
            success = False

        self.logger.info("A Publish will be created in ShotGrid and linked to:")
        self.logger.info("  %s" % (publish_path,))

        return success

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

        # Publish the file to the Material entity
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

        # Create a version for this publish to be linked to. If a version already exists,
        # update the version with this publish file
        publish_version = self._create_or_update_version(settings, item)
        item.properties["sg_version_data"] = publish_version
        item.properties["sg_version_number"] = publish_version_number

        # Upload the thumbnail to the Version and Material
        thumb = item.get_thumbnail_as_path()
        if thumb:
            if publish_version:
                self.parent.shotgun.upload_thumbnail("Version", publish_version["id"], thumb)
            entity = item.context.entity
            self.parent.shotgun.upload_thumbnail(entity["type"], entity["id"], thumb)
            self.logger.info("Uploaded thumbnail")

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

        publish_data = item.properties.sg_publish_data
        path = item.get_property("path")
        if publish_data and path:
            self.logger.info(
                "Publish created for file: %s" % (path,),
                extra={
                    "action_show_in_shotgun": {
                        "label": "Show Publish",
                        "tooltip": "Open the Publish in ShotGrid.",
                        "entity": publish_data,
                    }
                },
            )

    ############################################################################
    # Methods for creating/displaying custom plugin interface
    #

    def create_settings_widget(self, parent, items=None):
        """
        Creates a Qt widget, for the supplied parent widget (a container widget
        on the right side of the publish UI).

        :param parent: The parent to use for the widget being created.
        :param items: A list of PublishItems the selected publish tasks are parented to.
        :return: A QtGui.QWidget or subclass that displays information about
            the plugin and/or editable widgets for modifying the plugin's
            settings.
        """

        from sgtk.platform.qt import QtCore, QtGui

        if not items:
            return

        # Description widget
        description_group_box = super(MaterialPublishPlugin, self).create_settings_widget(parent, items)

        item = items[0]
        if not item.context.entity:
            return

        # Material entity info and options
        material_entity = self.parent.shotgun.find_one(
            "CustomNonProjectEntity01",
            filters=[["id", "is", item.context.entity["id"]]],
            fields=[
                "code",
                "sg_type",
                "tags",
                "sg_status_list",
                "sg_material_cost",
            ]
        )

        tags = ", ".join([tag["name"] for tag in material_entity.get("tags", [])]) or "Not set"
        status = material_entity.get("sg_status_list", "Not set")
        cost = material_entity.get("sg_material_cost", "Not set")

        material_label = QtGui.QLabel(parent)
        material_label.setTextFormat(QtCore.Qt.RichText)
        material_info = f"""
        <table>
            <tr>
                <td style="text-align: left">Name:</th>
                <td style="text-align: left">{material_entity.get("code", "Not set")}</td>
            </tr>
            <tr>
                <td style="text-align: left">Type:</th>
                <td style="text-align: left">{material_entity.get("sg_type", "Not set")}</td>
            </tr>
            <tr>
                <td style="text-align: left">Status:</th>
                <td style="text-align: left">{status}</td>
            </tr>
            <tr>
                <td style="text-align: left">Tags:</th>
                <td style="text-align: left">{tags}</td>
            </tr>
            <tr>
                <td style="text-align: left">Material Cost:</th>
                <td style="text-align: left">{cost}</td>
            </tr>
        </table>
        """
        material_label.setText(material_info)
        material_info_group_box = QtGui.QGroupBox(parent)
        material_info_group_box.setTitle("Material")
        material_info_layout = QtGui.QVBoxLayout()
        material_info_layout.addWidget(material_label)
        material_info_group_box.setLayout(material_info_layout)

        # The main widget
        widget = QtGui.QWidget(parent)
        widget_layout = QtGui.QVBoxLayout()
        widget_layout.addWidget(description_group_box)
        widget_layout.addWidget(material_info_group_box)
        widget.setLayout(widget_layout)
        return widget

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

        publish_template_setting = settings.get("Publish Material Template")

        if publish_template_setting:
            publish_template = self.parent.engine.get_template_by_name(
                publish_template_setting.value
            )
            if publish_template:
                return publish_template

        return item.get_property("publish_template")

    def get_publish_type(self, settings, item):
        """
        Get a publish type for the supplied settings and item.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish type for

        :return: A publish type or None if one could not be found.
        """

        # publish type explicitly set or defined on the item
        publish_type = item.get_property("publish_type")
        if publish_type:
            return publish_type

        # fall back to the path info hook logic
        publisher = self.parent
        path = item.get_property("path")
        if path is None:
            raise AttributeError("'PublishData' object has no attribute 'path'")

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

        # publish type explicitly set or defined on the item
        publish_path = item.get_property("publish_path")
        if publish_path:
            return publish_path

        publish_template = self.get_publish_template(settings, item)
        if publish_template:

            # First, try to get the template fields from the selected context. If no folder has
            # been created on disk, this logic will fail as the cache will be empty. We have to
            # find another solution to get the template keys from the current context
            try:
                fields = item.context.as_template_fields(publish_template, validate=True)
            except TankError:
                ctx_entity = item.context.task or item.context.entity or item.context.project
                self.parent.sgtk.create_filesystem_structure(ctx_entity["type"], ctx_entity["id"])
                fields = item.context.as_template_fields(publish_template, validate=True)

            # try to fill all the missing keys
            missing_keys = publish_template.missing_keys(fields)
            if missing_keys:
                self._extend_fields(settings, item, fields, missing_keys)

            if missing_keys:

                # TODO for publish at project context we may need to additionally find fields from the current publish path

                self.logger.warning("Not enough keys to apply publish fields (%s) "
                                    "to publish template (%s)" % (fields, publish_template))
                return

            publish_path = publish_template.apply_fields(fields)
            item.properties["publish_version"] = fields.get("version")

        item.properties["publish_path"] = publish_path

        return publish_path

    def get_publish_version(self, settings, item, version_name=None, fields=None):
        """Query for the Version entity."""

        if item.parent and "sg_version_data" in item.parent.properties:
            return item.parent.properties.sg_version_data

        fields = fields or []
        fields.extend(["id", "published_files", "code"])
        version_name = version_name or self.get_publish_name(settings, item)
        task = item.context.task
        entity = item.context.entity
        filters = [
            ["project", "is", self._get_project(item)],
            ["entity", "is", entity],
            ["sg_task", "is", task],
            ["code", "is", version_name],
        ]
        return self.parent.shotgun.find_one("Version", filters=filters, fields=fields)

    def get_publish_version_number(self, settings, item):
        """
        Get the publish version for the supplied settings and item.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish version for

        Extracts the publish version via the configured work template if
        possible. Will fall back to using the path info hook.
        """

        # publish version explicitly set or defined on the item
        publish_version_number = item.get_property("sg_version_number")
        if publish_version_number:
            return publish_version_number

        publish_version_number = self._get_next_published_file_version(settings, item)
        if publish_version_number is None:
            publish_version_number = 1

        return publish_version_number

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

    def get_publish_user(self, settings, item):
        """
        Get the user that will be associated with this publish.

        If publish_user is not defined as a ``property`` or ``local_property``,
        this method will return ``None``.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish template for

        :return: A user entity dictionary or ``None`` if not defined.
        """

        user = item.get_property("publish_user", default_value=None)
        if user:
            return user
        return sgtk.util.get_current_user(self.parent.sgtk)

    def get_publish_fields(self, settings, item):
        """
        Get additional fields that should be used for the publish. This
        dictionary is passed on to :meth:`tank.util.register_publish` as the
        ``sg_fields`` keyword argument.

        If publish_fields is not defined as a ``property`` or
        ``local_property``, this method will return an empty dictionary.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish template for

        :return: A dictionary of field names and values for those fields.
        """
        return item.get_property("publish_fields", default_value={})

    def get_publish_kwargs(self, settings, item):
        """
        Get kwargs that should be passed to :meth:`tank.util.register_publish`.
        These kwargs will be used to update the kwarg dictionary that is passed
        when calling :meth:`tank.util.register_publish`, meaning that any value
        set here will supersede a value already retrieved from another
        ``property`` or ``local_property``.

        If publish_kwargs is not defined as a ``property`` or
        ``local_property``, this method will return an empty dictionary.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish template for

        :return: A dictionary of kwargs to be passed to
                 :meth:`tank.util.register_publish`.
        """
        return item.get_property("publish_kwargs", default_value={})

    def get_publish_dependencies(self, settings, item):
        """
        Get publish dependencies for the supplied settings and item.

        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish template for

        :return: A list of file paths representing the dependencies to store in
            SG for this publish
        """

        # local properties first
        dependencies = item.local_properties.get("publish_dependencies")

        # have to check against `None` here since `[]` is valid and may have
        # been explicitly set on the item
        if dependencies is None:
            # get from the global item properties.
            dependencies = item.properties.get("publish_dependencies")

        if dependencies is None:
            # not set globally or locally on the item. make it []
            dependencies = []

        return dependencies

    ############################################################################
    # protected methods

    def _copy_to_publish_template(self, settings, item):
        """Copy the publish item to the publish tempalte path."""

        path = item.get_property("path")
        publish_path = self.get_publish_path(settings, item)
        if path != publish_path:
            try:
                publish_folder = os.path.dirname(publish_path)
                ensure_folder_exists(publish_folder)
                copy_file(path, publish_path)
            except Exception:
                raise Exception(
                    "Failed to copy work file from '%s' to '%s'.\n%s"
                    % (path, publish_path, traceback.format_exc())
                )

    def _get_next_published_file_version(self, settings, item):
        """
        Query ShotGrid to get the latest published file for the given item.

        :param item: :class`FileItem` object we want to get the latest published file for
        :type item: :class`FileItem`
        :param data_retreiver: If provided, the api request will be async. The default value
            will execute the api request synchronously.
        :type data_retriever: ShotgunDataRetriever

        :return: If the request is async, then the request task id is returned, else the
            published file data result from the api request.
        :rtype: str | dict
        """

        version = self.get_publish_version(settings, item)
        if not version:
            # Version does not exist, this will be the first published file 
            return 1

        if not version["published_files"]:
            # Version has no published files, this will be the first
            return 1

        publish_type = self.get_publish_type(settings, item)
        published_file_ids = [pf["id"] for pf in version["published_files"]]
        published_files_filters = [
            ["id", "in", published_file_ids],
            ["published_file_type.PublishedFileType.code", "is", publish_type],
        ]
        published_files_fields = ["version_number"]
        order = [{"field_name": "version_number", "direction": "desc"}]
        latest_published_file = self.parent.shotgun.find_one(
            "PublishedFile",
            filters=published_files_filters,
            fields=published_files_fields,
            order=order,
        )
        if not latest_published_file:
            # Did not find any published files, this will be the first of this kind
            return 1

        return latest_published_file["version_number"] + 1

    def _get_material_entity(self, entity, filters=None, fields=None):
        """Query for the Material in ShotGrid."""

        material_id = entity.get("id")
        material_type = entity.get("type")
        filters = filters or []
        filters.append(["id", "is", material_id])
        return self.parent.shotgun.find_one(
            material_type,
            filters=filters,
            fields=fields,
        )

    def _get_project(self, item):
        """Get the project for the item."""

        if item.context.project:
            return item.context.project

        # Else, default to the bundle project
        return self.parent.context.project

    def _extend_fields(self, settings, item, fields, missing_keys):
        """
        Add missing fields to match the publish template.
        :param settings: This plugin instance's configured settings
        :param item: The item to determine the publish path for
        :param fields: Templates fields extracted from the context
        :param missing_keys: List of missing fields keys
        :return:
        """

        # publish_name = self.get_publish_name(settings, item)
        path = item.get_property("path")
        filename = os.path.basename(path)
        name, file_extension = os.path.splitext(filename)
        file_extension = file_extension[1:]

        if "version" in missing_keys:
            version_number = self.get_publish_version_number(settings, item)
            if not version_number:
                version_number = 1
            fields["version"] = version_number
            missing_keys.remove("version")

        if "name" in missing_keys:
            fields["name"] = name
            missing_keys.remove("name")

        if "extension" in missing_keys:
            fields["extension"] = file_extension
            missing_keys.remove("extension")

    def _create_or_update_version(self, settings, item):
        """Create a new version for the published file, or update if it already exists."""

        publisher = self.parent

        # Check if the version exists already
        version_name = self.get_publish_name(settings, item)
        version = self.get_publish_version(settings, item, version_name)
        entity = item.context.entity
        if not version:
            self.logger.info("Creating Version...")
            task = item.context.task
            version_data = {
                "project": self._get_project(item),
                "code": version_name,
                "description": item.description,
                "entity": entity,
                "sg_task": task,
            }

            if "sg_publish_data" in item.properties:
                publish_data = item.properties["sg_publish_data"]
                version_data["published_files"] = [publish_data]

            # log the version data for debugging
            self.logger.debug(
                "Populated Version data...",
                extra={
                    "action_show_more_info": {
                        "label": "Version Data",
                        "tooltip": "Show the complete Version data dictionary",
                        "text": "<pre>%s</pre>" % (pprint.pformat(version_data),),
                    }
                },
            )

            # Create the version
            version = publisher.shotgun.create("Version", version_data)
            self.logger.info("Version created!")
        else:
            # Update the version
            version_data = {"published_files": version["published_files"] or []}
            if "sg_publish_data" in item.properties:
                publish_data = item.properties["sg_publish_data"]
                version_data["published_files"].append(publish_data)

            publisher.shotgun.update("Version", version["id"], version_data)
            self.logger.info("Version updated!")

            # Update the version data
            version.update(version_data)

        return version
