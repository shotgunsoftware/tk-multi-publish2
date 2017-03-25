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
import re

import sgtk

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
_MIMETYPES_LOOKUP_POPULATED = False


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

    logger = sgtk.platform.current_bundle().logger
    logger.debug("Getting file type info for extension: '%s'..." % (extension,))

    # iterate over the common extensions to find a known file type
    for (display_name, info) in _COMMON_EXTENSIONS.iteritems():
        ext_list = info[0]
        if extension.lower() in ext_list:
            logger.debug("Found common file type info: %s, %s" % info)
            return display_name, info[1]

    # if we're here, not a hardcoded, common type. check by category
    if is_audio(extension):
        info = "Audio File", "audio"
    elif is_image(extension):
        info = "Image File", "image"
    elif is_video(extension):
        info = "Video File", "video"
    else:
        # no matches. return the generic result
        info = "Generic File", "file"

    logger.debug("Best guess at file type info: %s, %s" % info)
    return info


def get_file_path_components(path):
    """
    Convenience method for determining file components for a given path.

    :param str path: The path to the file to componentize.

    Returns file path components in the form::

        # example 1: path="/path/to/the/file/my_file.v001.ext"

        {
            "path": "/path/to/the/file/my_file.v001.ext",
            "folder": "/path/to/the/file" ,
            "filename": "my_file.v001.ext",
            "filename_no_ext": "my_file.v001",
            "extension": "ext",
            "prefix": "my_file",
            "version": 1,
            "version_str": v001
        }

        # example 1: path="/path/to/the/file/my_file.ext"

        {
            "path": "/path/to/the/file/my_file.ext",
            "folder": "/path/to/the/file" ,
            "filename": "my_file.ext",
            "filename_no_ext": "my_file",
            "extension": "ext",
            "prefix": "my_file",
            "version": None,
            "version_str": None
        }

    """

    logger = sgtk.platform.current_bundle().logger
    logger.debug("Getting file path components for path: '%s'..." % (path,))

    # the easy bits
    (folder, filename) = os.path.split(path)
    (filename_no_ext, extension) = os.path.splitext(filename)

    # remove the "." from the extension
    extension = extension.lstrip(".")

    # some default values in case we can't determine a version
    prefix = filename_no_ext
    version_str = None
    version = None

    # now figure out if there's a version stashed in the name. this looks for a
    # pattern like "my_file.v###.ext" where #### is a version number. There may
    # be additional common version patterns that we need to add to this logic as
    # well.
    version_match = re.search("(.*)\.(v([0-9]+))\.[^.]+$", filename)

    if version_match:
        prefix = version_match.group(1)
        version_str = version_match.group(2)
        version = int(version_match.group(3))  # remove leading zeros

    file_info = dict(
        path=path,
        folder=folder,
        filename=filename,
        filename_no_ext=filename_no_ext,
        extension=extension,
        prefix=prefix,
        version=version,
        version_str=version_str,
    )

    logger.debug("Extracted file components: %s" % (file_info,))
    return file_info


def get_next_version_folder(folder, pattern="^v(\d{3})$"):
    """
    Returns the next available version subfolder within the supplied folder.

    :param str folder: The path path to a folder containing subfolders
        representing versions.
    :param str pattern: A regex pattern matching the version subfolders. The
        default value matches the letter "v" followed by a 3 digit padded
        version number. The pattern should match the entire subfolder name
        and should include one set of parenthesis to allow matching of the
        version number.

    :returns: An integer representing the next sequential version folder

    :raises ValueError: if the supplied folder does not exist.

    For example, if the supplied folder looks like this::

        /path/to/some/folder/publish/
            v001/
            v002/
            v003/

    The return value would be an integer, 4. If there are no subfolders or no
    folders matching the pattern, an integer value of 1 will be returned.
    """

    logger = sgtk.platform.current_bundle().logger
    logger.debug("Getting the next version subfolder for: %s" % (folder,))

    if not os.path.exists(folder):
        raise ValueError("The supplied folder does not exist: %s" % (folder,))

    # keep a running list of matched version numbers. at the end we'll return
    # the highest version + 1. So if we start with 0 and find nothing, we'll end
    # up with 1.
    existing_versions = [0]

    for subfolder_name in os.listdir(folder):

        # make sure we're only processing subfolders
        if not os.path.isdir(os.path.join(folder, subfolder_name)):
            continue

        version_match = re.match(pattern, subfolder_name)
        if version_match:
            # append the matched version number as an int to the list
            existing_versions.append(int(version_match.group(1)))

    # return the next available version
    return max(existing_versions) + 1


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

    global _MIMETYPES_LOOKUP_POPULATED

    # don't need to call this more than once.
    if _MIMETYPES_LOOKUP_POPULATED:
        return

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
            # lowercase everything we add to the lookup to address situations
            # such as jpg vs JPG
            _LOOKUP_BY_EXTENSION[category].append(ext.lower())

    _MIMETYPES_LOOKUP_POPULATED = True

# call once at import time
_build_mimetypes_lookup()


def _is_category(extension, category):
    """
    Returns True if the supplied extension is in the list of known extensions
    for the supplied category
    """

    # see if the extension is in the supplied category
    return ".%s" % (extension,) in _LOOKUP_BY_EXTENSION[category]
