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
from sgtk.util.filesystem import copy_file, copy_folder

# create a logger to use throughout
logger = sgtk.platform.get_logger(__name__)

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


# ---- file/path util functions

def copy_path_to_version(path, version, padding=3):
    """
    Makes a copy of the supplied path in the same directory, augmented with the
    supplied version.

    If the path is a folder, its contents will be copied into the new folder.

    Returns the copied path.

    Example 1::

        new_file = copy_path_to_version("/path/to/my_file.v001.ext", 2)
        print new_file
        # /path/to/my_file.v002.ext

    Example 2::

        new_folder = copy_path_to_version("/path/to/folder.v0001", 2, padding=4)
        print new_folder
        # /path/to/folder.v0002

    If the destination path already exists, no copy will occur and None will be
    returned.

    :param path: Path to copy.
    :param version: The version to copy the path to.
    :param padding: The number of digits to pad the version number.

    :return: The newly created path.

    :raises: ``Exception`` if the new version path already exists.
    """

    logger.debug("Copying path '%s' to version %s..." % (path, version))

    # break down the supplied path to its components in order to easily build
    # the new version path
    path_info = get_file_path_components(path)

    # build the new path from the supplied path components plus the new version
    padded_version = str(version).zfill(padding)
    new_name = "%s.v%s" % (path_info["prefix"], padded_version)
    if path_info["extension"]:
        new_name = "%s.%s" % (new_name, path_info["extension"])

    # construct the full path in the same folder
    new_path = os.path.join(path_info["folder"], new_name)
    logger.debug("New path: %s" % (new_path,))

    if os.path.exists(new_path):
        raise Exception(
            "Versioned destination path already exists: %s" % (new_path,))

    # now copy the source to the new path and return it
    if os.path.isdir(path):
        # folder
        copy_folder(path, new_path)
    else:
        # file
        copy_file(path, new_path)

    return new_path


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

        # example 1: file with version number
        # path="/path/to/the/file/my_file.v001.ext"

        {
            "path": "/path/to/the/file/my_file.v001.ext",
            "folder": "/path/to/the/file" ,
            "folder_name": "file",
            "filename": "my_file.v001.ext",
            "filename_no_ext": "my_file.v001",
            "extension": "ext",
            "prefix": "my_file",
            "version": 1,
            "version_str": v001,
            "version_padding": 3
        }

        # example 2: file without version number
        # path="/path/to/the/file/my_file.ext"

        {
            "path": "/path/to/the/file/my_file.ext",
            "folder": "/path/to/the/file" ,
            "folder_name": "file",
            "filename": "my_file.ext",
            "filename_no_ext": "my_file",
            "extension": "ext",
            "prefix": "my_file",
            "version": None,
            "version_str": None,
            "version_padding": None
        }

        # example 3: folder with version number
        # path="/path/to/the/folder.v001"

        {
            "path": "/path/to/the/folder.v001",
            "folder": "/path/to/the" ,
            "folder_name": "the",
            "filename": "folder.v001",
            "filename_no_ext": "folder.v001",
            "extension": None,
            "prefix": "folder",
            "version": 1,
            "version_str": v001,
            "version_padding": 3
        }

        # example 4: folder without version number
        # path="/path/to/the/folder"

        {
            "path": "/path/to/the/folder",
            "folder": "/path/to/the" ,
            "folder_name": "the",
            "filename": "folder",
            "filename_no_ext": "folder",
            "extension": None,
            "prefix": "folder",
            "version": None,
            "version_str": None,
            "version_padding": None
        }

    """

    # get the path in a normalized state. no trailing separator, separators are
    # appropriate for current os, no double separators, etc.
    path = sgtk.util.ShotgunPath.normalize(path)

    logger.debug("Getting file path components for path: '%s'..." % (path,))

    # break it up into the major components
    (folder, filename) = os.path.split(path)

    # extract the extension and remove the "."
    (filename_no_ext, extension) = os.path.splitext(filename)
    if extension:
        extension = extension.lstrip(".")
    else:
        # prevent extension = ""
        extension = None

    # the folder name is the name of the parent directory
    folder_name = os.path.split(folder)[-1]

    # see if there is a version in the filename. must match .v### somewhere in
    # the filename.
    version_pattern = re.compile("(.*)\.(v(\d+))\.[^.]+$", re.IGNORECASE)
    version_pattern_match = re.search(version_pattern, filename)
    if version_pattern_match:
        prefix = version_pattern_match.group(1)
        version_str = version_pattern_match.group(2)
        version = int(version_pattern_match.group(3))
        version_padding = len(version_str.lstrip("v"))
    else:
        # no version detected. set these to default state
        prefix = filename_no_ext
        version_str = None
        version = None
        version_padding = None

    if extension == version_str:
        # probably a folder of the form: folder.v001
        filename_no_ext = filename
        extension = None

    file_info = dict(
        path=path,
        folder=folder,
        folder_name=folder_name,
        filename=filename,
        filename_no_ext=filename_no_ext,
        extension=extension,
        prefix=prefix,
        version=version,
        version_str=version_str,
        version_padding=version_padding
    )

    logger.debug(
        "Extracted components from path '%s': %s" %
        (path, file_info)
    )
    return file_info


def get_image_sequence_paths(folder):
    """
    Given a folder, inspect the contained files to find what appear to be images
    with frame numbers.

    :param folder: The path to a folder potentially containing a sequence of
        images.

    :return: A list of paths for each identified image seuqence. For example:
        ["/path/to/the/supplied/folder/key_light1.%04d.exr",
         "/path/to/the/supplied/folder/fill_light1.%04d.exr"]

    """

    logger.debug("Looking for image sequences in folder: '%s'..." % (folder,))

    seq_paths = set()

    # list of filenames without the frame number to avoid unnecessary processing
    processed_names = []

    # examine the files in the folder
    for file in os.listdir(folder):

        file_path = os.path.join(folder, file)
        if os.path.isdir(file_path):
            # ignore this folder
            continue

        file_info = get_file_path_components(file_path)
        filename = file_info["filename"]

        type_info = get_file_type_info(file_info["extension"])

        # if the extension isn't an image type, no need to continue. the display
        # name in the type info will be something specific like "Rendered Image"
        # or "Image File". Should probably rethink this. feels fragile.
        if not "image" in type_info[0].lower():
            continue

        # looking for any number of digits between dots: .0001. or .0999.
        frame_pattern = re.compile("(\.(\d+)\.)")
        frame_pattern_match = re.search(frame_pattern, filename)

        if not frame_pattern_match:
            # no frame number detected. carry on.
            continue

        # build up a fram padding string to replace the frame number
        match_str = frame_pattern_match.group(1)
        frame_str = frame_pattern_match.group(2)

        # see if we've already processed this name (without the frame number)
        filename_no_frame = filename.replace(match_str, ".")
        if filename_no_frame in processed_names:
            continue

        # add this name to the list to avoid doing the steps below for a
        # different frame number
        processed_names.append(filename_no_frame)

        padding = len(frame_str)
        frame_format = ".%%0%dd." % (padding,)

        seq_filename = file_info["filename"].replace(match_str, frame_format)
        seq_path = os.path.join(file_info["folder"], seq_filename)

        logger.debug("Found image sequence: %s" % (seq_path,))
        seq_paths.add(seq_path)

    return list(seq_paths)


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


# ---- icon util

def get_builtin_icon(name):
    """
    Return an icon for the name supplied.

    If no matching icon can be found, a generic "file" icon will be
    returned.

    :param str names: The name of the icon to return.

    :return: The path to a found icon.
    """

    publisher = sgtk.platform.current_bundle()

    # the publisher's icons folder
    icons_folder = os.path.abspath(
        os.path.join(publisher.disk_location, "icons"))

    # try to find an icon for the supplied names
    icon_path = os.path.join(icons_folder, "%s.png" % (name,))
    if os.path.exists(icon_path):
        return icon_path

    # no match. return the file icon
    return os.path.join(icons_folder, "file.png")


# ---- publish util functions

def get_publishes(context, path, publish_name, filters=None):
    """
    Returns a list of SG published file dicts for any existing publishes that
    match the supplied context, path, and publish_name.

    :param context: The context to search publishes for
    :param path: The path to match against previous publishes
    :param publish_name: The name of the publish.
    :param filters: A list of additional SG find() filters to apply to the
        publish search.

    :return: A list of ``dict``s representing existing publishes that match
        the supplied arguments. The paths returned are the standard "id", and
        "type" as well as the "path" field.

    This method is typically used by publish plugin hooks to determine if there
    are existing publishes for a given context, publish_name, and path and
    warning appropriately.
    """

    publisher = sgtk.platform.current_bundle()

    logger.debug(
        "Getting other publishes for context: %s, path: %s, name: %s" %
        (context, path, publish_name)
    )

    # ask core to do a dry_run of a publish with the supplied criteria. this is
    # a workaround for our inability to filter publishes by path. so for now,
    # get a dictionary of data that would be used to create a matching publish
    # and use that to get publishes via a call to find(). Then we'll filter
    # those by their path field. Once we have the ability in SG to filter by
    # path, we can replace this whole method with a simple call to find().
    publish_data = sgtk.util.register_publish(
        publisher.sgtk,
        context,
        path,
        publish_name,
        version_number=None,
        dry_run=True
    )
    logger.debug("Publish dry run data: %s" % (publish_data,))

    # now build up the filters to match against
    publish_filters = filters or []
    for field in ["code", "entity", "name", "project", "task"]:
        publish_filters.append([field, "is", publish_data[field]])
    logger.debug("Build publish filters: %s" % (publish_filters,))

    # run the
    publishes = publisher.shotgun.find(
        "PublishedFile",
        publish_filters,
        ["path"]
    )

    # next, extract the publish path from each of the returned publishes and
    # compare it against the supplied path. if the paths match, we add the
    # publish to the list of publishes to return.
    logger.debug("Comparing publish paths...")
    matching_publishes = []
    for publish in publishes:
        publish_path = sgtk.util.resolve_publish_path(publisher.sgtk, publish)
        if publish_path and publish_path == path:
            matching_publishes.append(publish)

    return matching_publishes


def clear_status_for_other_publishes(context, publish_data):
    """
    Clear the status of any other publishes matching the supplied publish data.

    The loader app respects the status of publishes to determine which are
    available for the user to load in their DCC. Because it is possible to
    create a version entry in SG with the same path multiple times, this method
    provides an easy way to clear the status of previous publishes for a given
    path.

    The publish data supplied should be the fully populated publish data
    returned by a call to ``sgtk.util.register_publish()``.

    :param publish_data: Dictionary of the current publish data (i.e. the
        publish entry whose status will not be cleared).
    """

    publisher = sgtk.platform.current_bundle()

    logger.debug("Clearing the status of any other publishes.")

    # determine the path from the publish data. this will match the path that
    # was used to register the publish
    path = sgtk.util.resolve_publish_path(publisher.sgtk, publish_data)
    name = publish_data["name"]

    # get a list of all publishes matching this criteria
    publishes = get_publishes(
        context,
        path,
        name,
        filters=["sg_status_list", "is_not", None]
    )

    if not publishes:
        # no other publishes. nothing to do.
        logger.debug("No other publishes detected for path: %s" % (path,))
        return

    # do a batch update of the other publishes to clear their status
    batch_data = []
    for publish in publishes:

        # make sure we don't update the supplied publish
        if publish["id"] == publish_data["id"]:
            continue

        # add the update info to the batch data list
        batch_data.append({
            "request_type": "update",
            "entity_type": publish["type"],
            "entity_id": publish["id"],
            "data": {"sg_status_list": None}  # will clear the status
        })

    # execute all the updates!
    publisher.shotgun.batch(batch_data)


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
