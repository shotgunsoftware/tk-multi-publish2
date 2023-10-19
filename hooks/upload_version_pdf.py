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
import shutil

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class UploadVersionPDFPlugin(HookBaseClass):
    """Plugin for publishing translations to PDF."""

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """Convert the file to PDF and upload to ShotGrid."""

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

        The type string should be one of the data types that toolkit accepts as
        part of its environment configuration.
        """
        plugin_settings = {
            "Upload": {
                "type": "bool",
                "default": False,
                "description": "Upload PDF as Uploaded Movie to Version",
            },
        }
        all_settings = super(UploadVersionPDFPlugin, self).settings
        all_settings.update(plugin_settings)
        return all_settings

    @property
    def item_filters(self):
        """List of item types that this plugin is interested in."""

        return ["file.ppt"]

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

        return {"accepted": True, "checked": True}

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

        framework_office2pdf = self.load_framework("tk-framework-office2pdf_v0.x.x")
        if not framework_office2pdf:
            raise Exception("Missing required framework: tk-framework-office2pdf")

        framework_pdf2png = self.load_framework("tk-framework-pdf2png_v0.x.x")
        if not framework_pdf2png:
            raise Exception("Missing required framework: tk-framework-pdf2png")
        
        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        # Get the frameworks to translate PPT to PDF
        # NOTE these frameworks are not part of the standard Toolkit config
        framework_office2pdf = self.load_framework("tk-framework-office2pdf_v0.x.x")
        framework_pdf2png = self.load_framework("tk-framework-pdf2png_v0.x.x")

        # Get the translation file paths
        path = item.properties["path"]
        file_name = os.path.basename(path)
        base_file_name = os.path.splitext(file_name)[0]
        pdf_file_name = f"{base_file_name}.pdf"

        pdf_temp_dir = None
        png_temp_dir = None

        try:
            # Do the PPT to PDF translations, and upload as sg_translation_files
            pdf_temp_dir = framework_office2pdf.translate(path=path)
            pdf_file_path = os.path.join(pdf_temp_dir, pdf_file_name)
            if not os.path.exists(pdf_file_path):
                raise Exception(f"Failed to create PDF {pdf_file_name} from {file_name}")

            # Set item properties and create Version in ShotGrid for PDF file
            item.properties["path"] = pdf_file_path
            item.properties["publish_name"] = pdf_file_name
            super(UploadVersionPDFPlugin, self).publish(settings, item)

            # Make sure we have the version that was just created
            if not item.properties["sg_version_data"]["id"]:
                raise Exception("Failed to create Version for PDF")

            # Update the Version wtih the PDF content
            pdf_version_id = item.properties["sg_version_data"]["id"]
            pdf_version_type = item.properties["sg_version_data"]["type"]
            self.parent.engine.shotgun.upload(
                entity_type=pdf_version_type,
                entity_id=pdf_version_id,
                path=pdf_file_path,
                field_name="sg_translation_files"
            )
            self.parent.engine.shotgun.update(
                entity_type=pdf_version_type,
                entity_id=pdf_version_id,
                data={"sg_translation_type": "PDF"}
            )

            # Override the Version thumbnail wth the PDF thumbnail
            png_temp_dir = framework_pdf2png.translate(path=pdf_file_path)
            png_file_name = f"{base_file_name}.png"
            png_file_path = os.path.join(png_temp_dir, png_file_name)
            if os.path.exists(pdf_file_path):
                self.parent.engine.shotgun.upload_thumbnail(
                    entity_type=pdf_version_type,
                    entity_id=pdf_version_id,
                    path=png_file_path
                )
                # Optionally override the Pubilshed File thumbnail as well
                publish_data = item.properties["sg_publish_data"]
                if publish_data:
                    publish_id = publish_data["id"]
                    publish_type = publish_data["type"]
                    self.parent.engine.shotgun.upload_thumbnail(
                        entity_type=publish_type,
                        entity_id=publish_id,
                        path=png_file_path
                    )
            else:
                self.logger.warning(f"Failed to create PNG {png_file_name} from PDF {pdf_file_name}")
        finally:
            # Clean up temporary directories and files
            if os.path.exists(pdf_temp_dir):
                shutil.rmtree(pdf_temp_dir)
            if os.path.exists(png_temp_dir):
                shutil.rmtree(png_temp_dir)

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