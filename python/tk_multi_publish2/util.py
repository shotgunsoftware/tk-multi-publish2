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
import glob
import re

from sgtk.util.filesystem import ensure_folder_exists, copy_file


def prepare_for_publish(path):
    """
    Utility method used to prep a file for publish.

    :param str path: The path to the file to publish.

    Makes a snapshot of the file in a ``publish`` folder in the same directory
    as the file. Returns info for the publish snapshot file. The method also
    makes use of the ``get_next_version`` function to determine the next
    available version of the file in the ``publish`` directory.

    Returns publish file path info of the form::

        # source path is "/path/to/the/file/my_file.ext"
        {
            "path": "/path/to/the/file/publish/my_file.v0001.ext",
            "directory": "/path/to/the/file/publish",
            "filename": "my_file.v0001.ext",
            "filename_no_ext": "my_file.v0001",
            "prefix": "my_file",
            "version_str": "v0001",
            "version": 1,
            "extension": "ext"
        }

    """

    # TODO: consider the case where the supplied path already has a version
    #       number in it: "/path/to/the/file/my_file.v0001.ext"

    # extract the basic path components from the source path
    (source_directory, source_filename) = os.path.split(os.path.abspath(path))
    (prefix, extension) = os.path.splitext(source_filename)

    # remove the dot from the extension
    extension = extension.lstrip(".")

    # construct the publish directory path
    publish_directory = os.path.join(source_directory, "publish")

    # ensure the publish directory exists
    ensure_folder_exists(publish_directory)

    # get the next version to use for publishing
    version = get_next_version(publish_directory, prefix, extension)

    # formatted strings
    version_str = "v%04d" % (version,)
    filename_no_ext = "%s.%s" % (prefix, version_str)
    filename = "%s.%s" % (filename_no_ext, extension)

    # construct the ultimate publish path
    publish_path = os.path.join(publish_directory, filename)

    # snapshot the source file to the publish path
    copy_file(path, publish_path)

    # return a dictionary of info about the file to be published
    return dict(
        path=publish_path,
        directory=publish_directory,
        filename=filename,
        filename_no_ext=filename_no_ext,
        prefix=prefix,
        version_str=version_str,
        version=version,
        extension=extension,
    )


def get_next_version(folder, prefix, extension):
    """
    Identify and return the next available version number for the file with
    the supplied previx and extension in the supplied directory.

    :param str folder: The folder to find matching files
    :param str prefix: The file prefix to match against
    :param str extension: The file extension to match against

    :returns: An ``int`` corresponding to the next available version of the file

    Examines the supplied folder for files matching the format::

        <folder>/<prefix>.v####.<extension>

    Determines the next available version number and returns it as an int.
    """

    # start with a list of 0. if there are not matching files, then the
    # max will be 0, making the next available version 1.
    versions = [0]

    # build the full glob pattern
    file_pattern = "%s.v*.%s" % (prefix, extension)
    glob_pattern = os.path.join(folder, file_pattern)

    # build a regex pattern to extract the version number from matched files
    regex_str = os.path.join(folder, "%s\.v(\d+)\.%s" % (prefix, extension))
    regex = re.compile("^%s$" % (regex_str,))

    # find any files matching the glob, then search for the match string
    for previous_version in glob.glob(glob_pattern):
        match = re.match(regex, previous_version)
        if match:
            version = int(match.group(1))
            versions.append(version)

    return max(versions) + 1
