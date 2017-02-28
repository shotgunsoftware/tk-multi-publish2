# Copyright (c) 2017 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.
import sgtk
import os
import re

HookBaseClass = sgtk.get_hook_baseclass()


class GenericSceneCollector(HookBaseClass):
    """
    A generic collector that handles files and general objects.
    """

    def process_current_scene(self, parent_item):
        """
        Analyzes the current scene open in a DCC and parents a subtree of items
        under the parent_item passed in.

        :param parent_item: Root item instance
        """
        # default implementation does not do anything

    def process_file(self, parent_item, path):
        """
        Analyzes the given file and creates one or more items
        to represent it.

        :param parent_item: Root item instance
        :param path: Path to analyze
        :returns: The main item that was created
        """
        file_name = os.path.basename(path)
        (file_name_no_ext, file_extension) = os.path.splitext(file_name)

        if file_extension in [".jpeg", ".jpg", ".png"]:
            file_item = parent_item.create_item("file.image", "Image File", file_name)
            file_item.set_thumbnail_from_path(path)
            file_item.set_icon_from_path(os.path.join(self.disk_location, "icons", "image.png"))

        elif file_extension in [".mov", ".mp4"]:
            file_item = parent_item.create_item("file.movie", "Movie File", file_name)
            file_item.set_icon_from_path(os.path.join(self.disk_location, "icons", "quicktime.png"))

        else:
            file_item = parent_item.create_item("file", "Generic File", file_name)
            file_item.set_icon_from_path(os.path.join(self.disk_location, "icons", "page.png"))

        file_item.properties["extension"] = file_extension
        file_item.properties["path"] = path
        file_item.properties["filename"] = file_name

        # check if path matches pattern fooo.v123.ext
        version = re.search("(.*)\.v([0-9]+)\.[^\.]+$", file_name)
        if version:
            # strip all leading zeroes
            file_item.properties["prefix"] = version.group(1)
            version_no_leading_zeroes = version.group(2).lstrip("0")
            file_item.properties["version"] = int(version_no_leading_zeroes)
        else:
            file_item.properties["version"] = 0
            file_item.properties["prefix"] = file_name_no_ext

        return file_item


