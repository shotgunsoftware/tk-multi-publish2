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
import re

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()

# ---- globals

# a regular expression used to extract the version number from the file.
# this implementation assumes the version number is of the form 'v###'
# coming just before an optional extension in the file/folder name and just
# after a '.', '_', or '-'.
VERSION_REGEX = re.compile("(.*)([._-])v(\d+)\.?([^.]+)?$", re.IGNORECASE)

# a regular expression used to extract the frame number from the file.
# this implementation assumes the version number is of the form '.####'
# coming just before the extension in the filename and just after a '.', '_',
# or '-'.
FRAME_REGEX = re.compile("(.*)([._-])(\d+)\.([^.]+)$", re.IGNORECASE)


class BasicPathInfo(HookBaseClass):
    """
    Methods for basic file path parsing.
    """

    def get_publish_name(self, path):
        """
        Given a file path, return the display name to use for publishing.

        Typically, this is a name where the path and any version number are
        removed in order to keep the publish name consistent as subsequent
        versions are published.

        Example::

            # versioned file. remove the version
            in: /path/to/the/file/scene.v001.ma
            out: scene.ma

            # image sequence. replace the frame number with #s
            in: /path/to/the/file/my_file.001.jpg
            out: my_file.###.jpg

        :param path: The path to a file, likely one to be published.

        :return: A publish display name for the provided path.
        """

        publisher = self.parent

        logger = publisher.logger
        logger.debug("Getting publish name for path: %s ..." % (path,))

        path_info = publisher.util.get_file_path_components(path)
        filename = path_info["filename"]

        version_pattern_match = re.search(VERSION_REGEX, filename)
        frame_pattern_match = re.search(FRAME_REGEX, filename)

        if version_pattern_match:
            # found a version number, use the other groups to remove it
            prefix = version_pattern_match.group(1)
            extension = version_pattern_match.group(4) or ""
            if extension:
                publish_name = "%s.%s" % (prefix, extension)
            else:
                publish_name = prefix
        elif frame_pattern_match:
            # found a frame number, replace it with #s
            prefix = frame_pattern_match.group(1)
            frame_sep = frame_pattern_match.group(2)
            frame = frame_pattern_match.group(3)
            display_str = "#" * len(frame)
            extension = frame_pattern_match.group(4) or ""
            publish_name = "%s%s%s.%s" % (
                prefix, frame_sep, display_str, extension)
        else:
            publish_name = filename

        logger.debug("Returning publish name: %s" % (publish_name,))
        return publish_name

    def get_version_number(self, path):
        """
        Extract a version number from the supplied path.

        This is used by plugins that need to know what version number to
        associate with the file when publishing.

        :param path: The path to a file, likely one to be published.

        :return: An integer representing the version number in the supplied
            path. If no version found, ``None`` will be returned.
        """

        publisher = self.parent

        logger = publisher.logger
        logger.debug("Getting version number for path: %s ..." % (path,))

        path_info = publisher.util.get_file_path_components(path)
        filename = path_info["filename"]

        # default if no version number detected
        version_number = None

        # if there's a version in the filename, extract it
        version_pattern_match = re.search(VERSION_REGEX, filename)

        if version_pattern_match:
            version_number = int(version_pattern_match.group(3))

        logger.debug("Returning version number: %s" % (version_number,))
        return version_number

    def get_image_sequence_path(self, path):
        """
        Given a path to an image on disk, see if a frame number can be
        identified. If the frame number can be identified, return the original
        path with the frame number replaced by a format string with appropriate
        padding.

        Example::

             in: "/path/to/the/supplied/folder/key_light1.0001.exr"
            out: "/path/to/the/supplied/folder/key_light1.%04d.exr",

        :param path: The path to identify a frame number and return format path

        :return: A path with the frame number replaced by format specification.
            If no frame number exsists in the path, returns ``None``.
        """

        (folder, filename) = os.path.split(path)

        # see if the path has a frame number
        frame_pattern_match = re.search(FRAME_REGEX, filename)

        if not frame_pattern_match:
            # no frame number detected. nothing to do
            return None

        prefix = frame_pattern_match.group(1)
        frame_sep = frame_pattern_match.group(2)
        frame_str = frame_pattern_match.group(3)
        extension = frame_pattern_match.group(4)

        # make sure we maintain the same padding
        padding = len(frame_str)
        frame_format = "%%0%dd" % (padding,)
        seq_filename = "%s%s%s.%s" % (
            prefix, frame_sep, frame_format, extension)

        # build the path in the same folder
        return os.path.join(folder, seq_filename)

    def get_version_path(self, path, version):
        """
        Given a path without a version number, return the path with the supplied
        version number.

        If a version number is detected in the supplied path, the path will be
        returned as-is.

        :param path: The path to inject a version number.
        :param version: The version number to inject.

        :return: The modified path with the supplied version number inserted.
        """

        publisher = self.parent

        logger = publisher.logger
        logger.debug("Getting version %s of path: %s ..." % (version, path))

        path_info = publisher.util.get_file_path_components(path)
        filename = path_info["filename"]

        # see if there's a version in the supplied path
        version_pattern_match = re.search(VERSION_REGEX, filename)

        if version_pattern_match:
            # version number already in the path. return the original path
            return path

        (basename, ext) = os.path.splitext(filename)

        # construct the new filename with the version number inserted
        version_filename = "%s.%s%s" % (basename, version, ext)

        # construct the new, full path
        version_path = os.path.join(path_info["folder"], version_filename)

        logger.debug("Returning version path: %s" % (version_path,))
        return version_path

    def get_next_version_path(self, path):
        """
        Given a file path, return a path to the next version.

        This is typically used by auto-versioning logic in plugins that need to
        save the current work file to the next version number.

        If no version can be identified in the supplied path, ``None`` will be
        returned, indicating that the next version path can't be determined.

        :param path: The path to a file, likely one to be published.

        :return: The path to the next version of the supplied path.
        """

        publisher = self.parent

        logger = publisher.logger
        logger.debug("Getting next version of path: %s ..." % (path,))

        # default
        next_version_path = None

        path_info = publisher.util.get_file_path_components(path)
        filename = path_info["filename"]

        # see if there's a version in the supplied path
        version_pattern_match = re.search(VERSION_REGEX, filename)

        if version_pattern_match:
            prefix = version_pattern_match.group(1)
            version_sep = version_pattern_match.group(2)
            version_str = version_pattern_match.group(3)
            extension = version_pattern_match.group(4) or ""

            # make sure we maintain the same padding
            padding = len(version_str)

            # bump the version number
            next_version_number = int(version_str) + 1

            # create a new version string filled with the appropriate 0 padding
            next_version_str = "v%s" % (str(next_version_number).zfill(padding))

            new_filename = "%s%s%s" % (prefix, version_sep, next_version_str)
            if extension:
                new_filename = "%s.%s" % (new_filename, extension)

            # build the new path in the same folder
            next_version_path = os.path.join(path_info["folder"], new_filename)

        logger.debug("Returning next version path: %s" % (next_version_path,))
        return next_version_path
