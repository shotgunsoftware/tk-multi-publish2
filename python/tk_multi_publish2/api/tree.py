# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import traceback

import datetime
import json

import sgtk
from .item import PublishItem

logger = sgtk.platform.get_logger(__name__)


class PublishTree(object):
    """
    This class provides an interface for operating on a tree of items to be
    published. At a high level, the publish tree is structured like this:

    .. code-block:: text

        [root]
          [item] Item 1 (A Publish Item)
            [task] Publish to Shotgun
            [task] Upload Media
          [item] Item 2 (A Publish Item)
            [task] Publish to Shotgun
            [task] Upload Media
          [item] Item 3 (A Publish Item)
            [task] Publish to Shotgun
            [task] Upload Media
            [item] Item 4 (A Child Item)
              [task] Re-rez
              [task] Alternate Transcode

    The tree is composed of a hierarchy of items. Each item in the tree,
    excluding the root, can have associated tasks.

    Instances of this class are iterable, making traversal very easy:

    .. code-block:: python

        for item in publish_tree:
            # process the item...
            for task in item.tasks:
                # process the task

    The special, :py:attr:`~root_item` is exposed as a property on publish tree
    instances. The root item is not processed as part of the validation,
    publish, or finalize execution phases, but it can be used to house
    :py:attr:`~.api.PublishItem.properties` that are global to the publish tree
    itself. All top-level publish items have the :py:attr:`~root_item` as their
    parent and can store information there.

    For example, to collect a list of files to process after all publish tasks
    have completed (within the :meth:`~.base_hooks.PostPhaseHook.post_finalize`
    method of the :class:`~.base_hooks.PostPhaseHook`), you could do something
    like this:

    .. code-block:: python

        # in your publish plugin...

        def publish(self, settings, item):

            # do your publish...

            # remember the file to process later
            if item.parent.is_root:
                files = item.properties.setdefault("process_later", [])
                files.append(my_publish_file)

        # then, in your post_finalize...

        def post_finalize(publish_tree):

            # process files that were stored for later
            files = publish_tree.root_item.properties.get("process_later", [])

    The class also provides an interface for serialization and deserialization
    of tree instances. See the :meth:`~save_file` and
    :meth:`~load_file` methods.
    """

    __slots__ = ["_root_item"]

    # define a serialization version to allow backward compatibility if the
    # serialization method changes
    SERIALIZATION_VERSION = 1

    @classmethod
    def from_dict(cls, tree_dict):
        """
        Create a publish tree instance given the supplied dictionary. The
        supplied dictionary is typically the result of calling ``to_dict`` on
        a publish tree instance during serialization.
        """
        # This check is valid until we need to alter the way serialization is
        # handled after initial release. Once that happens, this should be
        # altered to handle the various versions separately with this as the
        # fallback when the serialization version is not recognized.
        serialization_version = tree_dict.get(
            "serialization_version", "<missing version>"
        )
        if serialization_version != cls.SERIALIZATION_VERSION:
            raise sgtk.TankError(
                "Unrecognized serialization version (%s) for serialized publish "
                "task. It is unclear how this could have happened. Perhaps the "
                "serialized file was hand edited? Please consult your pipeline "
                "TD/developer/admin." % serialization_version
            )

        new_tree = cls()
        new_tree._root_item = PublishItem.from_dict(
            tree_dict["root_item"], serialization_version
        )

        return new_tree

    @staticmethod
    def load_file(file_path):
        """
        This method returns a new :class:`~.PublishTree` instance by reading
        a serialized tree file from disk._sgtk_custom_type

        :param str file_path: The path to a serialized publish tree.
        :return: A :class:`~.PublishTree` instance
        """

        with open(file_path, "rb") as tree_file_obj:
            try:
                return PublishTree.load(tree_file_obj)
            except Exception as e:
                logger.error(
                    "Error trying to load publish tree from file '%s': %s"
                    % (file_path, e)
                )
                raise

    @staticmethod
    def load(file_obj):
        """
        Load a publish tree from a supplied file-like object.

        :param file file_obj: A file-like object
        :return: A :class:`~.PublishTree` instance
        """

        try:
            # Pass in a object hook so that certain Toolkit objects are restored back
            # from their serialized representation.
            return PublishTree.from_dict(
                sgtk.util.json.load(file_obj, object_hook=_json_to_objects)
            )
        except Exception as e:
            logger.error(
                "Error loading publish tree: %s\n%s" % (e, traceback.format_exc())
            )
            raise

    def __init__(self):
        """Initialize the publish tree instance."""

        # The root item is the sole parent of all top level publish items. It
        # has no use other than organization and provides an easy interface for
        # beginning iteration and accessing all top level items.
        self._root_item = PublishItem("__root__", "__root__", "__root__", parent=None)

    def __iter__(self):
        """Iterates over the tree, depth first."""

        # item's are recursively iterable. this will yield all items under the
        # root.
        for item in self._root_item.descendants:
            yield item

    def clear(self, clear_persistent=False):
        """
        Clears the tree of all items.

        :param bool clear_persistent: If ``True``, all items will be cleared
            from the tree, including persistent items. Default is ``False``,
            which will clear non-persistent items only.
        """

        # Create a list of children to remove, as we'll be iterating
        # on the very items we are removing!!
        for item in list(self._root_item.children):
            if clear_persistent or not item.persistent:
                self.remove_item(item)

    def pformat(self):
        """
        Returns a human-readable string representation of the tree, useful for
        debugging.

        This is the string printed by the :meth:`~pprint` method.
        """
        return self._format_tree(self._root_item)

    def pprint(self):
        """
        Prints a human-readable string representation of the tree, useful for
        debugging.

        Example:

        .. code-block:: python

            manager = publish_app.create_publish_manager()
            manager.collect_session()

            # print the collected tree to the shell
            manager.tree.pprint()

            [item] Item 1 (A Publish Item)
              [task] Publish to Shotgun
              [task] Upload Media
            [item] Item 2 (A Publish Item)
              [task] Publish to Shotgun
              [task] Upload Media
            [item] Item 3 (A Publish Item)
              [task] Publish to Shotgun
              [task] Upload Media
        """

        print(self.pformat())

    def remove_item(self, item):
        """
        Remove the supplied item from the tree.

        :param item: The :ref:`publish-api-item` instance to remove from the
            tree.
        """

        if item == self.root_item:
            raise sgtk.TankError("Removing the root item is not allowed.")

        # all other items should have a parent
        item.parent.remove_item(item)

    def save_file(self, file_path):
        """
        Save the serialized tree instance to disk at the supplied path.
        """

        with open(file_path, "w") as file_obj:
            try:
                self.save(file_obj)
            except Exception as e:
                logger.error("Error saving the publish tree to disk: %s" % (e,))
                raise

    def save(self, file_obj):
        """
        Writes a json-serialized representation of the publish tree to the
        supplied file-like object.
        """
        try:
            json.dump(
                self,
                file_obj,
                indent=2,
                # all non-ASCII characters in the output are escaped with \uXXXX sequences
                ensure_ascii=True,
                # Use a custom JSON encoder to certain Toolkit objects are converted into a
                # JSON
                cls=_PublishTreeEncoder,
            )
        except Exception as e:
            logger.error(
                "Error saving publish tree: %s\n%s" % (e, traceback.format_exc())
            )
            raise

    def to_dict(self):
        """
        Returns a dictionary representation of the publish tree. Typically used
        during serialization of the publish tree.
        """
        return {
            "root_item": self.root_item.to_dict(),
            "serialization_version": self.SERIALIZATION_VERSION,
        }

    @property
    def persistent_items(self):
        """A generator of all persistent items in the tree."""
        for item in self.root_item.children:
            if item.persistent:
                yield item

    @property
    def root_item(self):
        """Returns the root item of this tree."""
        return self._root_item

    ############################################################################
    # protected methods

    def _format_tree(self, parent_item, depth=0):
        """
        Depth first traversal and string formatting of the tree given a root
        node.

        :param parent_item: The item to begin with
        :param depth: The current depth of the traversal (used for indentation)
        """

        tree_str = ""

        for item in parent_item.children:

            # format the item itself
            tree_str += "%s[item] %s\n" % ((depth * 2) * " ", str(item))

            # now do the item's tasks
            for task in item.tasks:
                tree_str += "%s[task] %s\n" % (((depth * 2) + 2) * " ", str(task))

            # process the children as well
            tree_str += "%s" % (self._format_tree(item, depth=depth + 1),)

        return tree_str


class _PublishTreeEncoder(json.JSONEncoder):
    """
    Implements the json encoder interface for custom publish tree serialization.
    """

    def default(self, data):
        if isinstance(data, PublishTree):
            return data.to_dict()
        elif isinstance(data, sgtk.Template):
            return {"_sgtk_custom_type": "sgtk.Template", "name": data.name}
        elif type(data) is datetime.date:
            return {"_sgtk_custom_type": "datetime.date", "value": data.isoformat()}
        elif type(data) is datetime.datetime:
            return {"_sgtk_custom_type": "datetime.datetime", "value": data.isoformat()}
        else:
            return super().default(data)


def _json_to_objects(data):
    """
    Check if an dictionary is actually representing a Toolkit object and
    unserializes it.

    :param dict data: Data to parse.

    :returns: The original data passed in or the Toolkit object if one was found.
    :rtype: object
    """
    if data.get("_sgtk_custom_type") == "sgtk.Template":
        templates = sgtk.platform.current_engine().sgtk.templates
        if data["name"] not in templates:
            raise sgtk.TankError(
                "Template '{0}' was not found in templates.yml.".format(data["name"])
            )
        return templates[data["name"]]
    elif data.get("_sgtk_custom_type") == "datetime.date":
        return datetime.date.fromisoformat(data.get("value"))
    elif data.get("_sgtk_custom_type") == "datetime.datetime":
        return datetime.datetime.fromisoformat(data.get("value"))
    return data
