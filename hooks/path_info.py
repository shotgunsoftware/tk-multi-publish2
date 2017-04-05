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
# this implementation assumes the version number is of the form '.v###' and
# comes just before an optional extension in the file/folder name.
VERSION_REGEX = re.compile("(.*)\.v(\d+)\.?([^.]+)?$", re.IGNORECASE)

# a regular expression used to extract the frame number from the file.
# this implementation assumes the version number is of the form '.####' and
# comes just before the extension in the filename.
FRAME_REGEX = re.compile("(.*)\.(\d+)\.?([^.]+)$", re.IGNORECASE)


class BasicPathInfo(HookBaseClass):
    """
    Methods for basic file path parsing.
    """

    def get_next_version_path(self, path):
        """
        Given a file path, return a path to the next version.

        This is typically used by auto-versioning logic in plugins that make
        copies of files/folders post publish.

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
            version_str = version_pattern_match.group(2)
            extension = version_pattern_match.group(3) or ""

            # make sure we maintain the same padding
            padding = len(version_str)

            # bump the version number
            next_version_number = int(version_str) + 1

            # create a new version string filled with the appropriate 0 padding
            next_version_str = "v%s" % (str(next_version_number).zfill(padding))

            new_filename = "%s.%s" % (prefix, next_version_str)
            if extension:
                new_filename = "%s.%s" % (new_filename, extension)

            # build the new path in the same folder
            next_version_path = os.path.join(path_info["folder"], new_filename)

        logger.debug("Returning next version path: %s" % (next_version_path,))
        return next_version_path

    def get_publish_name(self, path):
        """
        Given a file path, return the display name to use for publishing.

        Typically, this is a name where the path and any version number are
        removed in order to keep the publish name consistent as subsequent
        versions are published.

        Example::

            in: /path/to/the/file/my_file.v001.jpg
            out: my_file.jpg

        :param path: The path to a file, likely one to be published.

        :return: A publish display name for the provided path.
        """

        publisher = self.parent

        logger = publisher.logger
        logger.debug("Getting publish name for path: %s ..." % (path,))

        path_info = publisher.util.get_file_path_components(path)
        filename = path_info["filename"]

        # if there's a version in the filename, extract it
        version_pattern_match = re.search(VERSION_REGEX, filename)

        if version_pattern_match:
            # found a version number, use the other groups to remove it
            prefix = version_pattern_match.group(1)
            extension = version_pattern_match.group(3) or ""
            if extension:
                publish_name = "%s.%s" % (prefix, extension)
            else:
                publish_name = prefix
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
            version_number = int(version_pattern_match.group(2))
            logger.debug("PATTERN MATCH: " + str(version_number))

        logger.debug("Returning version_number: %s" % (version_number,))
        return version_number

    def get_image_sequence_paths(self, folder):
        """
        Given a folder, inspect the contained files to find what appear to be
        images with frame numbers.

        :param folder: The path to a folder potentially containing a sequence of
            images.

        :return: A list of paths for each identified image seuqence.
            For example: ["/path/to/the/supplied/folder/key_light1.%04d.exr",
            "/path/to/the/supplied/folder/fill_light1.%04d.exr"]

        """

        publisher = self.parent

        logger = publisher.logger

        logger.debug(
            "Looking for image sequences in folder: '%s'..." % (folder,))

        seq_paths = set()

        # list of filenames without the frame number to avoid unnecessary
        # processing
        processed_names = []

        # examine the files in the folder
        for filename in os.listdir(folder):

            file_path = os.path.join(folder, filename)
            if os.path.isdir(file_path):
                # ignore subfolders
                continue

            # TODO: don't continue if the extension isn't an image type

            # see if there is a frame number
            frame_pattern_match = re.search(FRAME_REGEX, filename)

            if not frame_pattern_match:
                # no frame number detected. carry on.
                continue

            prefix = frame_pattern_match.group(1)
            frame_str = frame_pattern_match.group(2)
            extension = frame_pattern_match.group(3) or ""

            # filename without a frame number.
            file_no_frame = "%s.%s" % (prefix, extension)

            # see if we've already processed
            if file_no_frame in processed_names:
                continue

            # add this name to the list to avoid doing the steps below for a
            # different frame number
            processed_names.append(file_no_frame)

            # make sure we maintain the same padding
            padding = len(frame_str)
            frame_format = "%%0%dd" % (padding,)
            seq_filename = "%s.%s" % (prefix, frame_format)
            if extension:
                seq_filename = "%s.%s" % (seq_filename, extension)

            # build the path in the same folder
            seq_path = os.path.join(folder, seq_filename)

            logger.debug("Found image sequence: %s" % (seq_path,))
            seq_paths.add(seq_path)

        return list(seq_paths)
