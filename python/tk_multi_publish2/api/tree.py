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

import json

import sgtk
from .item import PublishItem

logger = sgtk.platform.get_logger(__name__)


class PublishTree(object):
    """
    This class provides an interface for operating on a tree of items to be
    published. At a high level, a publish tree might be structured like this::

        * root
            * item1
                * itemA
                * itemB
            * item2
                * itemC
            * item3
                * itemD
            ...

    Each item in the tree (excluding the root) can have associated tasks.

    The class also provides an interface for serialization and deserialization
    of tree instances.
    """

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
        new_tree = cls()
        new_tree._root_item = PublishItem.from_dict(
            tree_dict["root_item"],
            tree_dict["serialization_version"]
        )

        # TODO: set the root item context so that it can be inherited?

        return new_tree

    @staticmethod
    def load_file(file_path):
        """
        This method returns a new :class:`~.PublishTree` instance by reading
        a serialized tree file from disk.

        :param file_path: The path to a serialized publish tree.
        :return: A :class:`~.PublishTRee` instance
        """

        with open(file_path, "rb") as tree_file_obj:
            try:
                return PublishTree.load(tree_file_obj)
            except Exception, e:
                logger.error(
                    "Erorr trying to load publish tree from file: %s" % (e,)
                )
                raise

    @staticmethod
    def load(file_obj):
        """
        Load a publish tree from a supplied file-like object.
        """

        try:
            return json.load(file_obj, cls=_PublishTreeDecoder)
        except Exception, e:
            logger.error(
                "Error loading publish tree: %s\n%s" %
                (e, traceback.format_exc())
            )
            raise

    def __init__(self):
        """Initialize the publish tree instance."""

        # The root item is the sole parent of all top-level publish items. It
        # has no use other than organization and provides an easy interface for
        # beginning iteration and accessing all top-level items.
        self._root_item = PublishItem(
            "__root__",
            "__root__",
            "__root__",
            parent=None
        )

    def __iter__(self):
        """Iterates over the tree, depth first."""

        # item's are recursively iterable. this will yield all items under the
        # root.
        for item in self._root_item:
            yield item

    def clear(self, clear_persistent=False):
        """Clears the tree of all non-persistent items.

        :param bool clear_persistent: If ``True``, all items will be cleared
            from the tree, including persistent items.
        """

        for item in self._root_item.children:
            if clear_persistent or not item.persistent:
                self.remove_item(item)

    def pformat(self):
        """Returns a human-readable string representation of the tree"""
        return self._format_tree(self._root_item)

    def pprint(self):
        """Prints a human-readable string representation of the tree."""
        print self.pformat()

    def remove_item(self, item):
        """Remove the supplied item from the tree."""

        if item == self.root_item:
            raise sgtk.TankError("Removing the root item is not allowed.")

        # all other items should have a parent
        item.parent.remove_item(item)

    def save_file(self, file_path):
        """Save the tree to disk at the supplied path."""

        with open(file_path, "w") as file_obj:
            try:
                self.save(file_obj)
            except Exception, e:
                logger.error(
                    "Erorr saving the publish tree to disk: %s" % (e,)
                )
                raise

    def save(self, file_obj):
        """
        Write a json-serialized representation of the publish tree to the
        supplied file-like object.
        """

        try:
            json.dump(
                self,
                file_obj,
                indent=2,
                ensure_ascii=True,
                cls=_PublishTreeEncoder
            )
        except Exception, e:
            logger.error(
                "Error saving publish tree: %s\n%s" %
                (e, traceback.format_exc())
            )
            raise

    def to_dict(self):
        """
        Returns a dictionary representation of the publish tree. Typically used
        during serialization of the publish tree.
        """
        return {
            "root_item": self.root_item.to_dict(),
            "serialization_version": PublishTree.SERIALIZATION_VERSION
        }

    @property
    def items(self):
        """A depth-first generator of all items to be published."""
        for item in self._root_item:
            yield item

    @property
    def persistent_items(self):
        """Returns a list of persistent items in the tree."""
        return [i for i in self.root_item.children if i.persistent]

    @property
    def root_item(self):
        """Returns the root item of this tree."""
        return self._root_item

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
                tree_str += "%s[task] %s\n" % (
                    ((depth * 2) + 2) * " ", str(task))

            # process the children as well
            tree_str += "%s" % (self._format_tree(item, depth=depth+1),)

        return tree_str


class _PublishTreeEncoder(json.JSONEncoder):
    """
    Implements the json encoder interface for custom publish tree serialization.
    """
    def default(self, publish_tree):
        return publish_tree.to_dict()


class _PublishTreeDecoder(json.JSONDecoder):
    """
    Implements the json decoder interface for custom publish tree
    deserialization.
    """
    def decode(self, json_str):
        tree_dict = json.loads(json_str)
        return PublishTree.from_dict(tree_dict)
