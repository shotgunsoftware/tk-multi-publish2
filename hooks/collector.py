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

        engine = self.parent.engine
        engine.logger.debug("Processing file: %s" % (path,))

        # break down the path into the necessary pieces for processing
        components = self._get_file_path_components(path)

        ext = components["extension"]
        filename = components["filename"]

        if ext in [".jpeg", ".jpg", ".png"]:
            file_item = parent_item.create_item("file.image", "Image File", filename)
            file_item.set_thumbnail_from_path(path)
            file_item.set_icon_from_path(os.path.join(self.disk_location, "icons", "image.png"))

        elif ext in [".mov", ".mp4"]:
            file_item = parent_item.create_item("file.movie", "Movie File", filename)
            file_item.set_icon_from_path(os.path.join(self.disk_location, "icons", "quicktime.png"))

        else:
            file_item = parent_item.create_item("file", "Generic File", filename)
            file_item.set_icon_from_path(os.path.join(self.disk_location, "icons", "page.png"))

        # update the item's property dict with the file component parts
        file_item.properties.update(components)

        return file_item

    def _get_file_path_components(self, path):
        """
        Convenience method for determining file components for a given path.

        :param str path: The path to the file to componentize.

        Returns file path components in the form::

            path="/path/to/the/file/my_file.v0001.ext"

            {
                "path": "/path/to/the/file/my_file.v0001.ext",
                "directory": "/path/to/the/file" ,
                "filename": "my_file.v0001.ext",
                "filename_no_ext": "my_file.v0001",
                "prefix": "my_file",
                "version_str": "v0001",
                "version": 1,
                "extension": "ext"
            }

        If there is no version number:
            - ``prefix`` will be the ``filename_no_ext`` value
            - ``version_str`` will be ``""``
            - ``version`` will be ``0``
        """

        # the easy bits
        (directory, filename) = os.path.split(path)
        (filename_no_ext, extension) = os.path.splitext(filename)

        # some default values in case we can't determine a version
        prefix = filename_no_ext
        version_str = ""
        version = 0

        # now figure out if there's a version stashed in the name. this looks
        # for a pattern like "my_file.v####.ext" where #### is a version number.
        # there may be additional common version patterns that we need to add
        # to this logic as well.
        version_match = re.search("(.*)\.(v([0-9]+))\.[^.]+$", filename)
        if version_match:
            prefix = version_match.group(1)
            version_str = version_match.group(2)
            version = int(version_match.group(3))  # remove leading zeros

        return dict(
            path=path,
            directory=directory,
            filename=filename,
            filename_no_ext=filename_no_ext,
            prefix=prefix,
            version_str=version_str,
            version=version,
            extension=extension,
        )
