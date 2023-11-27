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

import sgtk
from sgtk import TankError

HookBaseClass = sgtk.get_hook_baseclass()


# import sys
# sys.path.append("C:\\python_libs")
# import ptvsd
# ptvsd.enable_attach()
# ptvsd.wait_for_attach()


class CreateVREDMaterialPublishPlugin(HookBaseClass):
    """Plugin for publishing VRED Materials to ShotGrid."""

    ############################################################################
    # standard publish plugin properties

    @property
    def icon(self):
        """Path to an png icon on disk."""

        return os.path.join(self.disk_location, "icons", "vred_material.png")

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """Create a VRED Material from the source AXF file, and publish it to ShotGrid. This plugin will create a VRED Material by running a local VRED install headless, in which it will load the AXF file and save it as as a VRED Material .osb file."""

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
        
        plugin_settings = {
            "Create Task": {
                "type": "bool",
                "default": True,
                "description": "Create a Digital Creation Task assigned to the current user. This helps streamline working on the VRED Material output in VRED.",
            },
            "Create VRED Asset": {
                "type": "bool",
                "default": True,
                "description": "Create a VRED Material Asset.",
            },
            "Create Render": {
                "type": "bool",
                "default": False,
                "description": "Create a VRED scene with geometry and apply the material to the geometry in the scene.",
            },
            "Render Template": {
                "type": "str",
                "default": os.path.join(
                    os.path.dirname(__file__),
                    "data",
                    "vred-render-template.vpb",
                ),
                "description": "If Create Render is True, optionally provide a template file to render.",
            },
            "Run VRED Headless": {
                "type": "bool",
                "default": True,
                "description": "If Run VRED Headless is True, VRED will create material without UI.",
            },
        }

        # Update the base settings with this plugin settings so that the base can be overriden
        # by this plugin (and not the reverse)
        base_settings = super(CreateVREDMaterialPublishPlugin, self).settings
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
            "*material.output",
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

        vred_path = self.get_vred_bin_path(item)
        if not vred_path:
            return {"accepted": True, "checked": False}

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

        vred_path = self.get_vred_bin_path(item)
        if not vred_path:
            error_msg = "VRED install required to create VRED Material."
            self.logger.error(error_msg)
            raise Exception(error_msg)

        if not self.is_material(item.context.entity):
            error_msg = "Entity Link must be set to a Material entity"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        publish_path = self.get_publish_path(settings, item)
        publish_file_path = os.path.join(publish_path, self._get_publish_file_name(settings, item))
        if os.path.exists(publish_file_path):
            error_msg = f"Publish file already exists {publish_file_path}."
            self.logger.warning(error_msg)
            raise Exception(error_msg)

        self.logger.info("A Publish will be created in ShotGrid and linked to:")
        self.logger.info("  %s" % (publish_file_path,))

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

        # Get upstream publish info from parent item
        version_number = item.parent.properties.get("sg_version_number")
        if not version_number:
            # Parent did not publish or failed to publish
            raise Exception("Missing upstream publish")

        path = item.parent.properties.get("sg_publish_data", {}).get("path", {}).get("local_path")
        if path:
            item.properties["path"] = path
        else:
            # Parent did not publish or failed to publish
            raise Exception("Missing upstream publish")

        # ---- determine the information required to publish

        # We allow the information to be pre-populated by the collector or a
        # base class plugin. They may have more information than is available
        # here such as custom type or template settings.

        publish_name = self.get_publish_name(settings, item)
        # publish_version = self.get_publish_version_number(settings, item)
        publish_version = version_number
        publish_path = self.get_publish_path(settings, item)
        publish_dependencies_paths = self.get_publish_dependencies(settings, item)
        publish_user = self.get_publish_user(settings, item)
        publish_fields = self.get_publish_fields(settings, item)
        publish_kwargs = self.get_publish_kwargs(settings, item)

        publish_file_name = self._get_publish_file_name(settings, item)
        publish_file_path = os.path.join(publish_path, publish_file_name)

        # FIXME cannot use get_publish_type because it uses the source publish path, which is an AXF
        # publish_type = self.get_publish_type(settings, item)
        publish_type = "VRED Material"

        # ---- trigger VRED to convert the AXF material to an OSB file

        # Ensure the VRED Material publish path exists to save to
        publisher.ensure_folder_exists(publish_path)

        if settings.get("Create Render").value:
            render_path = os.path.join(publish_path, "vred_render")
            render_geometry_path = settings.get("Render Template").value
            publisher.ensure_folder_exists(render_path)
        else:
            render_path = None
            render_geometry_path = None

        create_vred_asset = settings.get("Create VRED Asset").value

        # TODO auto generate a thumbnail if none set by user
        # TODO add tags to material asset in create vred material script
        # build the path to the VRED file and make sure the output directory exist
        hide_gui = settings.get("Run VRED Headless").value
        self._create_vred_material(
            item, publish_path, publish_name, render_path, render_geometry_path, create_vred_asset, hide_gui
        )

        # ---- publish the VRED Material to ShotGrid (main published file)

        publish_dependencies_ids = []
        if "sg_publish_data" in item.parent.properties:
            publish_dependencies_ids.append(
                item.parent.properties.sg_publish_data["id"]
            )

        if "sg_version_data" in item.parent.properties:
            version = item.parent.properties.sg_version_data
            version_data = {"id": version["id"], "type": version["type"], "name": version["code"]}
        else:
            error_msg = "Failed to get Version for publish file output"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        publish_data = {
            "tk": publisher.sgtk,
            "context": item.context,
            "comment": item.description,
            "path": publish_file_path,
            "name": publish_name,
            "created_by": publish_user,
            "version_number": publish_version,
            # This way we don't get proper version numbers when stacked
            # "version_number": 1,  # Assumes the upstream published file is created, so this output will be the first
            "thumbnail_path": item.get_thumbnail_as_path(),
            "published_file_type": publish_type,
            "dependency_paths": publish_dependencies_paths,
            "dependency_ids": publish_dependencies_ids,
            "sg_fields": publish_fields,
            "version_entity": version_data,
        }

        # add extra kwargs
        publish_data.update(publish_kwargs)

        # Only publish the file path if a new .osb file was created
        if os.path.exists(publish_file_path):
            self.logger.info("Registering publish...")

            # log the publish data for debugging
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

            # create the publish and stash it in the item properties for other
            # plugins to use.
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

        # ---- publish the VRED Material Asset files

        if create_vred_asset:
            # Modify publish data for the VRED Material Asset
            full_name = publish_data["name"]
            base_name, _ = os.path.splitext(full_name)
            material_asset_name = f"MAT_{base_name}"
            material_asset_path = os.path.join(
                os.path.dirname(publish_data["path"]),
                material_asset_name,
            )
            publish_data["path"] = material_asset_path
            publish_data["published_file_type"] = "VRED Material Asset"
            sgtk.util.register_publish(**publish_data)
            self.logger.info("Published VRED Material Asset!")

        # ---- publish the VRED render files
        if render_path:
            self._publish_vred_render(settings, item, publish_data, publish_name, render_path)

        # ---- create Task for VRED Material

        if settings.get("Create Task").value:
            material_entity = self._get_material_entity(
                item.context.entity,
                fields=["sg_project"]
            )
            self._create_task_for_vred_material(settings, item, material_entity, publish_user)

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

        publish_data = item.get_property("sg_publish_data")
        if not publish_data:
            return

        path = item.get_property("path")
        if path is None:
            raise AttributeError("'PublishData' object has no attribute 'path'")

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

        # This creates the PathCache entry so that the first time Workfiles encounters this
        # entity, it will be able to start working immediately on it (without settings up
        # folders or giving an error).
        # NOTE test turning this off at first
        # self._create_folders_if_needed(settings, item)

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

        # Plugin description
        description_group_box = QtGui.QGroupBox(parent)
        description_group_box.setTitle("Description:")

        # The publish plugin that subclasses this will implement the
        # `description` property. We'll use that here to display the plugin's
        # description in a label.
        description_label = QtGui.QLabel(self.description)
        description_label.setWordWrap(True)
        description_label.setOpenExternalLinks(True)

        # create the layout to use within the group box
        description_layout = QtGui.QVBoxLayout()
        description_layout.addWidget(description_label)
        description_layout.addStretch()
        description_group_box.setLayout(description_layout)

        # Create Version settings
        create_task_checkbox = QtGui.QCheckBox("Create Task for VRED Material output", parent)
        run_vred_headless_checkbox = QtGui.QCheckBox("Run VRED Headless", parent)
        create_vred_asset_checkbox = QtGui.QCheckBox("Create VRED Material Asset", parent)
        create_vred_render_checkbox = QtGui.QCheckBox("Create VRED Render of Material", parent)
        render_geometry_path_label = QtGui.QLabel("Render Template", parent)
        render_geometry_path_line_edit = QtGui.QLineEdit(parent)
        render_geometry_path_line_edit.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred,
        )
        render_geometry_path_file_chooser_button = QtGui.QPushButton("...", parent)
        render_geometry_path_file_chooser_button.setMaximumWidth(25)
        render_geometry_path_file_chooser_button.setSizePolicy(
            QtGui.QSizePolicy.Maximum,
            QtGui.QSizePolicy.Preferred,
        )
        render_geometry_path_file_chooser_button.clicked.connect(
            lambda checked=None, le=render_geometry_path_line_edit: le.setText(
                QtGui.QFileDialog.getOpenFileName(
                    parent,
                    "Choose File",
                    "/home",
                    "All Supoorted Files (*.vpe *.vpb *.osb)"
                )[0]
            )
        )
        render_geometry_layout = QtGui.QHBoxLayout()
        render_geometry_layout.addWidget(render_geometry_path_label)
        render_geometry_layout.addWidget(render_geometry_path_line_edit)
        render_geometry_layout.addWidget(render_geometry_path_file_chooser_button)
        render_geometry_path_widget = QtGui.QWidget(parent)
        render_geometry_path_widget.setLayout(render_geometry_layout)

        create_vred_render_checkbox.stateChanged.connect(
            lambda state: render_geometry_path_widget.setEnabled(state == QtCore.Qt.Checked)
        )

        vred_material_group_box_layout = QtGui.QVBoxLayout()
        vred_material_group_box_layout.addWidget(create_task_checkbox)
        vred_material_group_box_layout.addWidget(run_vred_headless_checkbox)
        vred_material_group_box_layout.addWidget(create_vred_asset_checkbox)
        vred_material_group_box_layout.addWidget(create_vred_render_checkbox)
        vred_material_group_box_layout.addWidget(render_geometry_path_widget)
        vred_material_group_box = QtGui.QGroupBox(parent)
        vred_material_group_box.setTitle("VRED Material Output Options")
        vred_material_group_box.setLayout(vred_material_group_box_layout)

        # The main widget
        widget = QtGui.QWidget(parent)
        widget_layout = QtGui.QVBoxLayout()

        widget_layout.addWidget(description_group_box)
        widget_layout.addWidget(vred_material_group_box)

        # Set the widget layout
        widget.setLayout(widget_layout)

        # Store any widgets whose value needs to be retrieved or set
        widget.setProperty("create_task_checkbox", create_task_checkbox)
        widget.setProperty("run_vred_headless_checkbox", run_vred_headless_checkbox)
        widget.setProperty("create_vred_asset_checkbox", create_vred_asset_checkbox)
        widget.setProperty("create_vred_render_checkbox", create_vred_render_checkbox)
        widget.setProperty("render_geometry_path_line_edit", render_geometry_path_line_edit)

        return widget

    def get_ui_settings(self, widget, items=None):
        """
        This method is required to be defined in order for the custom UI to show up in the app.

        Invoked by the Publisher when the selection changes. This method gathers the settings
        on the previously selected task, so that they can be later used to repopulate the
        custom UI if the task gets selected again. They will also be passed to the accept, validate,
        publish and finalize methods, so that the settings can be used to drive the publish process.

        The widget argument is the widget that was previously created by
        `create_settings_widget`.

        The method returns a dictionary, where the key is the name of a
        setting that should be updated and the value is the new value of that
        setting. Note that it is up to you how you want to store the UI's state as
        settings and you don't have to necessarily to return all the values from
        the UI. This is to allow the publisher to update a subset of settings
        when multiple tasks have been selected.

        Example::

            {
                 "setting_a": "/path/to/a/file"
            }

        :param widget: The widget that was created by `create_settings_widget`
        """

        ui_settings = {}

        # Get the Version Type settings value from the UI combobox
        create_task_checkbox = widget.property("create_task_checkbox")
        create_task = create_task_checkbox.isChecked()
        ui_settings["Create Task"] = create_task

        run_vred_headless_checkbox = widget.property("run_vred_headless_checkbox")
        headless = run_vred_headless_checkbox.isChecked()
        ui_settings["Run VRED Headless"] = headless

        # Get the Create VRED Asset settings value from the UI combobox
        create_vred_asset_checkbox = widget.property("create_vred_asset_checkbox")
        create_asset = create_vred_asset_checkbox.isChecked()
        ui_settings["Create VRED Asset"] = create_asset

        # Get the Create Render settings value from the UI combobox
        create_vred_render_checkbox = widget.property("create_vred_render_checkbox")
        create_render = create_vred_render_checkbox.isChecked()
        ui_settings["Create Render"] = create_render

        if create_render:
            render_geometry_path_line_edit= widget.property("render_geometry_path_line_edit")
            render_geometry_path = render_geometry_path_line_edit.text()
            ui_settings["Render Template"] = render_geometry_path

        return ui_settings

    def set_ui_settings(self, widget, settings, items=None):
        """
        This method is required to be defined in order for the custom UI to show up in the app.

        Allows the custom UI to populate its fields with the settings from the
        currently selected tasks.

        The widget is the widget created and returned by
        `create_settings_widget`.

        A list of settings dictionaries are supplied representing the current
        values of the settings for selected tasks. The settings dictionaries
        correspond to the dictionaries returned by the settings property of the
        hook.

        Example::

            settings = [
            {
                 "seeting_a": "/path/to/a/file"
                 "setting_b": False
            },
            {
                 "setting_a": "/path/to/a/file"
                 "setting_b": False
            }]

        The default values for the settings will be the ones specified in the
        environment file. Each task has its own copy of the settings.

        When invoked with multiple settings dictionaries, it is the
        responsibility of the custom UI to decide how to display the
        information. If you do not wish to implement the editing of multiple
        tasks at the same time, you can raise a ``NotImplementedError`` when
        there is more than one item in the list and the publisher will inform
        the user than only one task of that type can be edited at a time.

        :param widget: The widget that was created by `create_settings_widget`.
        :param settings: a list of dictionaries of settings for each selected
            task.
        :param items: A list of PublishItems the selected publish tasks are parented to.
        """

        if not settings:
            return

        if len(settings) > 1:
            raise NotImplementedError

        create_task_checkbox  = widget.property("create_task_checkbox")
        checked = settings[0].get("Create Task")
        create_task_checkbox.setChecked(checked)

        run_vred_headless_checkbox  = widget.property("run_vred_headless_checkbox")
        checked = settings[0].get("Run VRED Headless")
        run_vred_headless_checkbox.setChecked(checked)

        create_vred_asset_checkbox  = widget.property("create_vred_asset_checkbox")
        checked = settings[0].get("Create VRED Asset")
        create_vred_asset_checkbox.setChecked(checked)

        create_vred_render_checkbox  = widget.property("create_vred_render_checkbox")
        checked = settings[0].get("Create Render")
        create_vred_render_checkbox.setChecked(checked)

        render_geometry_path_line_edit = widget.property("render_geometry_path_line_edit")
        path = settings[0].get("Render Template")
        render_geometry_path_line_edit.setText(path)

    ############################################################################
    # Helper methods
    #

    def get_vred_bin_path(self, item):
        """
        Get the path to the VRED executable to use when creating the new scene

        :param item: Item to process
        :return: The path to the VRED executable
        """

        vred_bin_path = item.get_property("vred_bin_path")
        if vred_bin_path:
            return vred_bin_path

        engine_name = "tk-vred"
        launcher = sgtk.platform.create_engine_launcher(
            self.parent.sgtk, item.context, engine_name
        )
        software_versions = launcher.scan_software()

        vred_bin_path = software_versions[-1].path if software_versions else None 
        item.properties["vred_bin_path"] = vred_bin_path

        return vred_bin_path

    def _get_publish_file_name(self, settings, item):
        """Return the filename for the publish output.""" 

        file_name = self.get_publish_name(settings, item)
        base_file_name, _ = os.path.splitext(file_name)
        return f"{base_file_name}.osb"

    # def _create_folders_if_needed(self, settings, item):
    #     """Create the schema folders for the context and entity, if needed."""

    #     # NOTE on publish, names wtih space are replaced with dashes in this folder creation

    #     ctx = item.context
    #     template = self.get_publish_template(settings, item)

    #     create_folders = False
    #     try:
    #         # try to get all context fields from the template.  If this raises a TankError then this
    #         # is a sign that we need to create folders.
    #         ctx_fields = ctx.as_template_fields(template, validate=True)

    #         # ok, so we managed to get all fields but we still need to check that the context part
    #         # of the path exists on disk.  To do this, find the template that only contains context
    #         # keys:
    #         ctx_keys = set(ctx_fields)
    #         ctx_template = template
    #         while ctx_template:
    #             template_keys = set(
    #                 [k for k in ctx_template.keys if not ctx_template.is_optional(k)]
    #             )
    #             if template_keys <= ctx_keys:
    #                 # we've found the longest template that contains only context fields
    #                 break
    #             ctx_template = ctx_template.parent

    #         if not ctx_template:
    #             # couldn't figure out the path to test so assume that we need to create folders:
    #             create_folders = True
    #         else:
    #             # build the context path:
    #             ctx_path = ctx_template.apply_fields(ctx_fields)
    #             # and check that it exists:
    #             if not os.path.exists(ctx_path):
    #                 create_folders = True
    #     except TankError as e:
    #         # assume that we need to create folders!
    #         create_folders = True

    #     if create_folders:
    #         self._create_folders(ctx)

    # def _create_folders(self, ctx):
    #     """Create folders for specified context """

    #     # (AD) - does this work with non-standard hierarchies? e.g. /Task/Entity?
    #     ctx_entity = ctx.task or ctx.entity or ctx.project

    #     # FIXME: The launcher uses the defer_keyword setting, which allows to use keywords other
    #     # than the engine instance name, which is the default value in the launch app. Using
    #     # engine.instance_name is the best we can do at the moment because the is no way for workfiles
    #     # to now what the launcher app would have set when launching directly into that environment.
    #     #
    #     # Possible solutions:
    #     # - Using an app level defer_keyword setting might work, but it it may make sharing
    #     # settings through includes more difficult.
    #     # - Using an engine level defer_keyword setting might be a better approach,
    #     # since an app launcher instance launches a specific engine instance using a given defer_keyword.
    #     # In theory you could have multiple app launcher instances all launching the same engine
    #     # instance but with different defer_keywords for the same context, but that might be the
    #     # most absolute of edge cases.
    #     # - Look for the settings of the launcher app in the destination context and extract the
    #     # defer_keyword setting and reuse it.
    #     #
    #     # It may very well be that there's no solution that fits everyone and might warrant
    #     # a hook.
    #     self.parent.sgtk.create_filesystem_structure(
    #         ctx_entity.get("type"),
    #         ctx_entity.get("id"),
    #         engine=self.parent.engine.instance_name,
    #     )

    def _create_vred_material(
            self, item, publish_path, render_name, render_path, render_geometry_path, create_vred_asset, hide_gui=True
        ):
        """Run VRED headless to convert the AXF to OSB."""

        # reset the PYTHONPATH to avoid conflict with SG Desktop libraries
        # we won't need to have toolkit paths in PYTHONPATH because we won't run the engine nor any toolkit
        # operations
        env = os.environ.copy()
        env.pop("PYTHONPATH")
        # Add the env vars for the script
        env["VRED_MATERIAL_AXF_PATH"] = item.properties["path"]
        env["VRED_MATERIAL_OSB_PATH"] = publish_path
        env["VRED_MATERIAL_RENDER_NAME"] = render_name or ""
        env["VRED_MATERIAL_RENDER_PATH"] = render_path or ""
        env["VRED_MATERIAL_RENDER_GEOMETRY_PATH"] = render_geometry_path or ""
        env["VRED_MATERIAL_CREATE_ASSET"] = "1" if create_vred_asset else "0"

        create_vred_material_script = os.path.join(
            os.path.dirname(__file__), "scripts", "create_vred_material.py"
        )

        cmd = [
            self.get_vred_bin_path(item),
            create_vred_material_script,
            "-fast_start",
            "-console",
            "-insecure_python",
        ]
        if hide_gui:
            cmd.append("-hide_gui")

        import subprocess
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
        )
        p_output, _ = p.communicate()

        if p.returncode != 0:
            self.logger.error(p_output)
            raise Exception(f"Failed to create VRED Material.\n{p_output}")

    def _create_task_for_vred_material(self, settings, item, material_entity, publish_user):
        """create Task for VRED Material."""

        publisher = self.parent

        digital_creation_step = publisher.shotgun.find_one(
            "Step",
            filters=[
                ["entity_type", "is", item.context.entity["type"]],
                ["code", "is", "Material"],
            ],
        )
        task_name = "Create VRED Material"
        task = publisher.shotgun.find_one(
            "Task",
            filters=[
                ["entity", "is", material_entity],
                ["step", "is", digital_creation_step],
                ["content", "is", task_name],
            ],
            fields=["task_assignees"],
        )

        if task:
            if publish_user:
                # Update assigned users if current user not assigned
                update = True
                for assignee in task["task_assignees"]:
                    if assignee["id"] == publish_user["id"]:
                        update = False
                        break
                if update:
                    task_data = {"task_assignees": task["task_assignees"] + [publish_user]}
                    publisher.shotgun.update(task["type"], task["id"], task_data)
        else:
            # Create task
            task_data = {
                "content": task_name,
                "project": material_entity["sg_project"] or self._get_project(item),
                "entity": material_entity,
                "task_assignees": [publish_user],
                "step": digital_creation_step,
            }
            publisher.shotgun.create("Task", task_data)

    def _publish_vred_render(self, settings, item, publish_data, render_name, render_path):
        """Publish the files created by the VRED render."""

        publisher = self.parent
        publish_name = publish_data.get("name")

        # Create a version for the VRED render
        version_data = {
            "project": self._get_project(item),
            "code": publish_name,
            "description": item.description,
            "entity": item.context.entity,
            "sg_task": item.context.task,
            "sg_path_to_frames": render_path,
            "sg_version_type": "VRED Render",
        }
        version = publisher.shotgun.create("Version", version_data)

        render_file_path = os.path.join(
            render_path,
            f"{render_name}-00000.png",
        )
        if os.path.exists(render_file_path):
            publisher.shotgun.upload_thumbnail(
                version["type"], version["id"], render_file_path
            )
            publisher.shotgun.upload_filmstrip_thumbnail(
                version["type"], version["id"], render_file_path
            )
        
        render_movie_path = os.path.join(
            render_path,
            f"{render_name}.avi",
        )
        if os.path.exists(render_movie_path):
            publisher.shotgun.upload(
                version["type"],
                version["id"],
                render_movie_path,
                "sg_uploaded_movie",
            )

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
