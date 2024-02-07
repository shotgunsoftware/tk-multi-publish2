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
import pprint

import sgtk

# create a logger to use throughout
logger = sgtk.platform.get_logger(__name__)


# ---- file/path util functions


def get_version_path(path, version):
    """
    Given a path without a version number, return the path with the supplied
    version number.

    If a version number is detected in the supplied path, the path will be
    returned as-is.

    :param path: The path to inject a version number.
    :param version: The version number to inject.

    :return: The modified path with the supplied version number inserted.
    """

    # the logic for this method lives in a hook that can be overridden by
    # clients. exposing the method here in the publish utils api prevents
    # clients from having to call other hooks directly in their
    # collector/publisher hook implementations.
    publisher = sgtk.platform.current_bundle()
    return publisher.execute_hook_method(
        "path_info", "get_version_path", path=path, version=version
    )


def get_next_version_path(path):
    """
    Given a file path, return a path to the next version.

    This is typically used by auto-versioning logic in plugins that need to
    save the current work file to the next version number.

    If no version can be identified in the supplied path, ``None`` will be
    returned, indicating that the next version path can't be determined.

    :param path: The path to a file, likely one to be published.

    :return: The path to the next version of the supplied path.
    """

    # the logic for this method lives in a hook that can be overridden by
    # clients. exposing the method here in the publish utils api prevents
    # clients from having to call other hooks directly in their
    # collector/publisher hook implementations.
    publisher = sgtk.platform.current_bundle()
    return publisher.execute_hook_method(
        "path_info", "get_next_version_path", path=path
    )


def get_file_path_components(path):
    """
    Convenience method for determining file components for a given path.

    :param str path: The path to the file to componentize.

    Returns file path components in the form::

        # path="/path/to/the/file/my_file.v001.ext"

        {
            "path": "/path/to/the/file/my_file.v001.ext",
            "folder": "/path/to/the/file" ,
            "filename": "my_file.v001.ext",
            "extension": "ext",
        }

        # path="/path/to/the/folder"

        {
            "path": "/path/to/the/folder",
            "folder": "/path/to/the" ,
            "filename": "folder",
            "extension": None,
        }

    """

    # get the path in a normalized state. no trailing separator, separators are
    # appropriate for current os, no double separators, etc.
    path = sgtk.util.ShotgunPath.normalize(path)

    logger.debug("Getting file path components for path: '%s'..." % (path,))

    # break it up into the major components
    (folder, filename) = os.path.split(path)

    if os.path.isdir(path):
        # folder
        extension = None
    else:
        # file. extract the extension and remove the "."
        (_, extension) = os.path.splitext(filename)
        if extension:
            extension = extension.lstrip(".")
        else:
            # prevent extension = ""
            extension = None

    file_info = dict(
        path=path,
        folder=folder,
        filename=filename,
        extension=extension,
    )

    logger.debug("Extracted components from path '%s': %s" % (path, file_info))

    return file_info


def get_frame_sequence_path(path, frame_spec=None):
    """
    Given a path with a frame number, return the sequence path where the frame
    number is replaced with a given frame specification such as ``{FRAME}`` or
    ``%04d`` or ``$F``.

    :param path: The input path with a frame number
    :param frame_spec: The frame specification to replace the frame number with.

    :return: The full frame sequence path
    """

    # the logic for this method lives in a hook that can be overridden by
    # clients. exposing the method here in the publish utils api prevents
    # clients from having to call other hooks directly in their
    # collector/publisher hook implementations.
    publisher = sgtk.platform.current_bundle()
    return publisher.execute_hook_method(
        "path_info", "get_frame_sequence_path", path=path, frame_spec=frame_spec
    )


def get_frame_sequences(folder, extensions=None, frame_spec=None):
    """
    Given a folder, inspect the contained files to find what appear to be
    files with frame numbers.

    :param folder: The path to a folder potentially containing a sequence of
        files.

    :param extensions: A list of file extensions to retrieve paths for.
        If not supplied, the extension will be ignored.

    :param frame_spec: A string to use to represent the frame number in the
        return sequence path.

    :return: A list of tuples for each identified frame sequence. The first
        item in the tuple is a sequence path with the frame number replaced
        with the supplied frame specification. If no frame spec is supplied,
        a python string format spec will be returned with the padding found
        in the file.


        Example::

            get_frame_sequences(
                "/path/to/the/folder",
                ["exr", "jpg"],
                frame_spec="{FRAME}"
            )

            [
                (
                    "/path/to/the/supplied/folder/key_light1.{FRAME}.exr",
                    [<frame_1_path>, <frame_2_path>, ...]
                ),
                (
                    "/path/to/the/supplied/folder/fill_light1.{FRAME}.jpg",
                    [<frame_1_path>, <frame_2_path>, ...]
                )
            ]
    """

    # the logic for this method lives in a hook that can be overridden by
    # clients. exposing the method here in the publish utils api prevents
    # clients from having to call other hooks directly in their
    # collector/publisher hook implementations.
    publisher = sgtk.platform.current_bundle()
    return publisher.execute_hook_method(
        "path_info",
        "get_frame_sequences",
        folder=folder,
        extensions=extensions,
        frame_spec=frame_spec,
    )


def get_publish_name(path, sequence=False):
    """
    Given a file path, return the display name to use for publishing.

    Typically, this is a name where the path and any version number are removed
    in order to keep the publish name consistent as subsequent versions are
    published.

    Example::

        in: /path/to/the/file/my_file.v001.jpg
        out: my_file.jpg

    :param path: The path to a file, likely one to be published.
    :param sequence: If True, treat the path as a sequence name and replace
        the frame number with placeholder

    :return: A publish display name for the provided path.
    """

    # the logic for this method lives in a hook that can be overridden by
    # clients. exposing the method here in the publish utils api prevents
    # clients from having to call other hooks directly in their
    # collector/publisher hook implementations.
    publisher = sgtk.platform.current_bundle()
    return publisher.execute_hook_method(
        "path_info", "get_publish_name", path=path, sequence=sequence
    )


def get_version_number(path):
    """
    Extract a version number from the supplied path.

    This is used by plugins that need to know what version number to associate
    with the file when publishing.

    Example::

        in: /path/to/the/file/my_file.v001.jpg
        out: 1

    :param path: The path to a file, likely one to be published.

    :return: An integer representing the version number in the supplied path.
        If no version found, ``None`` will be returned.
    """

    # the logic for this method lives in a hook that can be overridden by
    # clients. exposing the method here in the publish utils api prevents
    # clients from having to call other hooks directly in their
    # collector/publisher hook implementations.
    publisher = sgtk.platform.current_bundle()
    return publisher.execute_hook_method("path_info", "get_version_number", path=path)


# ---- publish util functions


def get_conflicting_publishes(context, path, publish_name, filters=None):
    """
    Returns a list of PTR published file dicts for any existing publishes that
    match the supplied context, path, and publish_name.

    :param context: The context to search publishes for
    :param path: The path to match against previous publishes
    :param publish_name: The name of the publish.
    :param filters: A list of additional PTR find() filters to apply to the
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
        "Getting conflicting publishes for context: %s, path: %s, name: %s"
        % (context, path, publish_name)
    )

    # ask core to do a dry_run of a publish with the supplied criteria. this is
    # a workaround for our inability to filter publishes by path. so for now,
    # get a dictionary of data that would be used to create a matching publish
    # and use that to get publishes via a call to find(). Then we'll filter
    # those by their path field. Once we have the ability in PTR to filter by
    # path, we can replace this whole method with a simple call to find().
    publish_data = sgtk.util.register_publish(
        publisher.sgtk, context, path, publish_name, version_number=None, dry_run=True
    )
    logger.debug("Publish dry run data: %s" % (publish_data,))

    # now build up the filters to match against
    publish_filters = [filters] if filters else []
    for field in ["code", "entity", "name", "project", "task"]:
        publish_filters.append([field, "is", publish_data[field]])
    logger.debug("Build publish filters: %s" % (publish_filters,))

    # run the
    publishes = publisher.shotgun.find("PublishedFile", publish_filters, ["path"])

    # ensure the path is normalized for comparison
    normalized_path = sgtk.util.ShotgunPath.normalize(path)

    # next, extract the publish path from each of the returned publishes and
    # compare it against the supplied path. if the paths match, we add the
    # publish to the list of publishes to return.
    logger.debug("Comparing publish paths...")
    matching_publishes = []
    for publish in publishes:
        publish_path = sgtk.util.resolve_publish_path(publisher.sgtk, publish)
        if publish_path:
            # ensure the published path is normalized for comparison
            normalized_publish_path = sgtk.util.ShotgunPath.normalize(publish_path)
            if normalized_path == normalized_publish_path:
                matching_publishes.append(publish)

    return matching_publishes


def clear_status_for_conflicting_publishes(context, publish_data):
    """
    Clear the status of any conflicting publishes matching the supplied publish
    data.

    The loader app respects the status of publishes to determine which are
    available for the user to load in their DCC. Because it is possible to
    create a version entry in PTR with the same path multiple times, this method
    provides an easy way to clear the status of previous publishes for a given
    path.

    The publish data supplied should be the fully populated publish data
    returned by a call to ``sgtk.util.register_publish()``.

    :param publish_data: Dictionary of the current publish data (i.e. the
        publish entry whose status will not be cleared).
    """

    publisher = sgtk.platform.current_bundle()

    logger.debug("Clearing the status of any conflicting publishes.")

    # determine the path from the publish data. this will match the path that
    # was used to register the publish
    path = sgtk.util.resolve_publish_path(publisher.sgtk, publish_data)
    name = publish_data["name"]

    # get a list of all publishes matching this criteria
    publishes = get_conflicting_publishes(
        context, path, name, filters=["sg_status_list", "is_not", None]
    )

    if not publishes:
        # no conflicting publishes. nothing to do.
        logger.debug("No conflicting publishes detected for path: %s" % (path,))
        return

    # do a batch update of the conflicting publishes to clear their status
    batch_data = []
    for publish in publishes:

        # make sure we don't update the supplied publish
        if publish["id"] == publish_data["id"]:
            continue

        # add the update info to the batch data list
        batch_data.append(
            {
                "request_type": "update",
                "entity_type": publish["type"],
                "entity_id": publish["id"],
                "data": {"sg_status_list": None},  # will clear the status
            }
        )

    if batch_data:
        logger.debug("Batch updating publish data: %s" % (pprint.pformat(batch_data),))

        # execute all the updates!
        publisher.shotgun.batch(batch_data)


def get_thumbnail(path, context):
    """
    Given a path and context, attempt to automatically generate a thumbnail.

    :param path: The path to generate a thumbnail from.
    :param context: The context to help determine engine software locations in order to
        discover thumbnail extraction tools.

    :return: The generated thumbnail.
    :rtype: QtGui.QPixmap
    """

    # the logic for this method lives in a hook that can be overridden by
    # clients. exposing the method here in the publish utils api prevents
    # clients from having to call other hooks directly in their
    # collector/publisher hook implementations.
    publisher = sgtk.platform.current_bundle()
    return publisher.execute_hook_method(
        "thumbnail_generator", "generate_thumbnail", input_path=path, context=context
    )
