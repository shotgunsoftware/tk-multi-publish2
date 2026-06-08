# Copyright (c) 2025 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class FlowDesktopFileCollector(HookBaseClass):
    """
    Collector that operates on the Flow Production Tracking Desktop publish
    workflow. Should inherit from the basic collector hook in the
    ``tk-multi-publish2`` app. The collector setting for this hook should look
    something like this::

        collector: "{self}/collector.py:{self}/flowam/collector_desktop.py"

    """

    def process_file(self, settings, parent_item, path):
        """
        Analyzes the given file or folder and creates publish items.
        Blocks DCC-specific files that must be published from within their applications.

        Args:
            settings (dict): Configured settings for this collector
            parent_item: Root item instance
            path: Path of the file

        Returns:
            The created file item, or None if path is a folder or blocked DCC file
        """

        # Check if this is a DCC file that should not be published from desktop
        file_info = self.parent.util.get_file_path_components(path)
        extension = file_info["extension"]

        # Define DCC file extensions that cannot be published from desktop
        # These files require their specific DCC application to be open for proper publishing
        dcc_extensions = [
            # Maya
            "ma",
            "mb",
            # Nuke
            "nk",
            "nkple",
            # Houdini
            "hip",
            "hipnc",
            "hiplc",
            # 3ds Max
            "max",
            # Hiero
            "hrox",
            # Photoshop
            "psd",
            "psb",
            # VRED
            "vpb",
            "vpe",
            "osb",
            # Alias
            "wire",
            # After Effects
            "aep",
            "aet",
        ]

        if extension in dcc_extensions:
            # Get the file type display name
            file_type = "Unknown"
            for display_name, type_info in self.common_file_info.items():
                if extension in type_info["extensions"]:
                    file_type = display_name
                    break

            # Log an error message that will be visible to the user
            self.logger.error(
                "Cannot publish {file_type} files from Desktop. "
                "Please publish from within the application instead.".format(
                    file_type=file_type
                ),
                extra={
                    "action_show_more_info": {
                        "label": "Learn More",
                        "text": (
                            "<b>DCC files must be published from within their application.</b><br><br>"
                            "Files like Maya scenes (.ma, .mb), Nuke scripts (.nk, .nkple), Houdini scenes "
                            "(.hip, .hipnc, .hiplc), 3ds Max scenes (.max), Photoshop images (.psd, .psb), "
                            "and other DCC-specific formats contain application-specific data that requires "
                            "the DCC to be open for proper publishing.<br><br>"
                            "The Desktop Publisher is designed for publishing rendered images, textures, "
                            "Alembic caches, and other standalone files."
                        ),
                    }
                },
            )
            return None

        return self._collect_file(parent_item, path)
