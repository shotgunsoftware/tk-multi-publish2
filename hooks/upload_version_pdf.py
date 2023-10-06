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

        # TODO custom accept logic
        return super(UploadVersionPDFPlugin, self).accept(settings, item)

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

        # TODO custom validation logic
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
        name = os.path.splitext(file_name)[0]
        pdf_file_name = f"{name}.pdf"
        target_file = f"{version_id}.pdf"

        # Do the PPT to PDF translations, and upload as sg_translation_files
        temp_dir = framework_office2pdf.translate(path=path)
        source_file = os.path.join(temp_dir, pdf_file_name)
        target_file = os.path.join(temp_dir, target_file)
        os.rename(source_file, target_file)

        # Create the Version in ShotGrid
        # Update the item path to the pdf file path
        item.properties["path"] = target_file
        # Set the publish name before creating version so tht this version get
        # a more accurate version name
        item.properties["publish_name"] = f"{name}.pdf"
        # Call the parent plugin to do the Version creation
        super(UploadVersionPDFPlugin, self).publish(settings, item)
        if not item.properties["sg_version_data"]:
            # NOTE could create a Version if not already created
            raise Exception("Required Version to publish PDF translation.")

        # Update the Version wtih the PDF content
        version_id = item.properties["sg_version_data"]["id"]
        version_type = item.properties["sg_version_data"]["type"]
        publish_data = item.properties["sg_publish_data"]
        self.parent.engine.shotgun.upload(
            entity_type=version_type,
            entity_id=version_id,
            path=target_file,
            field_name="sg_translation_files"
        )
        self.parent.engine.shotgun.update(
            entity_type=version_type,
            entity_id=version_id,
            data={"sg_translation_type": "PDF"}
        )

        # Override the Version thumbnail wth the PDF thumbnail
        png_tmpdir = framework_pdf2png.translate(path=target_file)
        png_file = os.path.join(png_tmpdir, f"{version_id}.png")
        self.parent.engine.shotgun.upload_thumbnail(
            entity_type=version_type,
            entity_id=version_id,
            path=png_file
        )
        # Optionally override the Pubilshed File thumbnail as well
        if publish_data:
            publish_id = publish_data["id"]
            publish_type = publish_data["type"]
            self.parent.engine.shotgun.upload_thumbnail(
                entity_type=publish_type,
                entity_id=publish_id,
                path=png_file
            )

        # Clean up temporary directories and files
        shutil.rmtree(temp_dir)
        shutil.rmtree(png_tmpdir)

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