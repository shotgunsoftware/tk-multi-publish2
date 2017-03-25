# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import mimetypes
import os
import glob
import re
import time

from sgtk.util.filesystem import ensure_folder_exists, copy_file


# ---- globals

# populated by _build_mimetypes_lookup() below
_LOOKUP_BY_EXTENSION = {
    "audio": [],
    "image": [],
    "video": [],
}

# common extensions. provide a more descriptive title.
_COMMON_EXTENSIONS = {
    "3ds Max File": (["max"], "3dsmax"),
    "Alembic Cache": (["abc"], "alembic"),
    "Hiero File": (["hrox"], "hiero"),
    "Houdini OTL": (["otl"], "houdini"),
    "Houdini File": (["hip", "hipnc"], "houdini"),
    "Maya File": (["ma", "mb"], "maya"),
    "Movie File": (["mov", "mp4"], "movie"),
    "Nuke Script": (["nk"], "nuke"),
    "Photoshop Image": (["psd", "psb"], "photoshop"),
    "Rendered Image": (["dpx", "exr"], "render"),
}

# flag to indicate if the mimetypes extension lookup has been populated
_MIMIETYPES_LOOKUP_POPULATED = False


# ---- util functions

def get_file_type_info(extension):
    """
    Returns a tuple of file type info for the supplied extension.

    :param str extension: A file extension

    Example return data::

        # extesion == "ma"
        ("Maya Scene", "maya")

    The first value can be used to display the file type. The second value is a
    one word name that can be used to specify a more specific type. The name
    also typically corresponds to the base name of an icon available on the
    publisher.

    If no common type info can be found, returns None.
    """

    # iterate over the common extensions to find a known file type
    for (display_name, info) in _COMMON_EXTENSIONS.iteritems():
        ext_list = info[0]
        if extension.lower() in ext_list:
            return display_name, info[1]

    # if we're here, not a hardcoded, common type. check by category
    if is_audio(extension):
        return "Audio File", "audio"
    elif is_image(extension):
        return "Image File", "image"
    elif is_video(extension):
        return "Video File", "video"
    else:
        # no matches. return the generic result
        return "Generic File", "file"


def get_file_path_components(path):
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

    # remove the "." from the extension
    extension = extension.lstrip(".")

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


def prepare_for_publish(path, version=None):
    """
    Utility method used to prep a file for publish.

    :param str path: The path to the file to publish.
    :param version: ``str`` or ``int`` to override the version number used
        for the publish file.

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

    If the ``version`` override is provided, the next available version will be
    overridden by that value.

    Once the publish path is constructed, if a file already exists in the
    destination with that name, a timestamp is attached to the end of the
    file prefix.
    """

    # TODO: consider writing here:
    #       /path/to/the/file/publish/v0001/my_file.ext
    #  Would avoid issues with current studio file naming conventions
    #  Would require a better concept of versioning? i.e. explicit in publisher

    # TODO: consider the case where the supplied path already has a version
    #       number in it: "/path/to/the/file/my_file.v0001.ext"

    # TODO: consider optional arg to write to a publish subfolder
    #       /path/to/the/file/publish/<subfolder>/my_file.ext
    #  Would be nice for secondary files like alembic caches or playblasts

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
    if not version:
        version = get_next_version(publish_directory, prefix, extension)

    # formatted strings
    version_str = "v%04d" % (version,)
    filename_no_ext = "%s.%s" % (prefix, version_str)
    filename = "%s.%s" % (filename_no_ext, extension)

    # construct the ultimate publish path
    publish_path = os.path.join(publish_directory, filename)

    # check to see if path already exits. If so, tack on a timestamp.
    if os.path.exists(publish_path):
        timestamp = time.strftime('%Y%m%d%H%M%S')
        filename = "%s_%s.%s" % (filename_no_ext, timestamp, extension)
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


def is_audio(extension):
    """
    Returns True if the extension is a known audio file type.
    """
    return _is_category(extension, "audio")


def is_image(extension):
    """
    Returns True if the extension is a known image file type.
    """
    return _is_category(extension, "image")


def is_video(extension):
    """
    Returns True if the extension is a known video file type.
    """
    return _is_category(extension, "video")


# ---- helper functions

def _build_mimetypes_lookup():
    """
    Build lists of extensions by type.
    """

    # build the full list of common types from the system
    mimetypes.init()

    # iterate over all the known extensions
    for ext in mimetypes.types_map:

        # extract the category of this mimetype.
        # ex: the "image" portion of "image/jpeg"
        category = mimetypes.types_map[ext].split('/')[0]

        # the categories we're interested in are defined as keys by the lookup.
        # if this is one of those categories, add the extension to the list
        if category in _LOOKUP_BY_EXTENSION:
            # lowercase everything we add to the lookup to adress situations
            # such as jpg vs JPG
            _LOOKUP_BY_EXTENSION[category].append(ext.lower())


def _is_category(extension, category):
    """
    Returns True if the supplied extension is in the list of known extensions
    for the supplied category
    """

    global _MIMIETYPES_LOOKUP_POPULATED

    # cache the mimetypes if not done so already
    if not _MIMIETYPES_LOOKUP_POPULATED:
        _build_mimetypes_lookup()
        _MIMIETYPES_LOOKUP_POPULATED = True

    # see if the extension is in the supplied category
    return ".%s" % (extension,) in _LOOKUP_BY_EXTENSION[category]
