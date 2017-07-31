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
import sgtk
import tempfile
from sgtk.platform.qt import QtCore, QtGui

logger = sgtk.platform.get_logger(__name__)


class Item(object):
    """
    An object representing an scene or file item that should be processed.
    Items are constructed and returned by the collector hook.

    Items are organized as a tree with access to parent and children.
    """

    def __init__(self, item_type, display_type, name, parent):
        """
        Items should always be generated via the :meth:`Item.create_item` factory
        method and never created via the constructor.

        :param str item_type: Item type, typically following a hierarchical dot notation.
            For example, 'file', 'file.image', 'file.quicktime' or 'maya_scene'
        :param str display_type: Equivalent to the type, but for display purposes.
        :param str name: The name to represent the item in a UI.
            This can be a node name in a DCC or a file name.
        :param Item parent: Parent item.
        """
        self._name = name
        self._type = item_type
        self._display_type = display_type
        self._parent = parent
        self._thumb_pixmap = None
        self._icon_pixmap = None
        self._children = []
        self._tasks = []
        self._context = None
        self._properties = {}
        self._parent = None
        self._icon_path = None
        self._description = None
        self._created_temp_files = []
        self._bundle = sgtk.platform.current_bundle()
        self._checked = True
        self._enabled = True
        self._expanded = True
        self._thumbnail_enabled = True

    def __repr__(self):
        """
        String representation
        """
        if self._parent:
            return "<Item %s|%s:%s>" % (self._parent, self._type, self._name)
        else:
            return "<Item %s:%s>" % (self._type, self._name)

    def __del__(self):
        """
        Destructor
        """
        # clean up temp files created
        for temp_file in self._created_temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception, e:
                    logger.warning(
                        "Could not remove temporary file '%s': %s" % (temp_file, e)
                    )
                else:
                    logger.debug("Removed temp file '%s'" % temp_file)

    @classmethod
    def create_invisible_root_item(cls):
        """
        Creates a root under which items can be parented.

        :returns: :class:`Item`
        """
        return Item("_root", "_root", "_root", parent=None)

    def remove_item(self, item):
        """
        Takes out the given child item from the list of children
        """
        new_children = []
        for child in self._children:
            if child != item:
                new_children.append(child)
        self._children = new_children

    def is_root(self):
        """
        Checks if the current item is the root

        :returns: True if the root item, False otherwise
        """
        return self.parent is None

    def create_item(self, item_type, display_type, name):
        """
        Factory method for generating new items.

        :param str item_type: Item type, typically following a hierarchical dot notation.
            For example, 'file', 'file.image', 'file.quicktime' or 'maya_scene'
        :param str display_type: Equivalent to the type, but for display purposes.
        :param str name: The name to represent the item in a UI.
            This can be a node name in a DCC or a file name.
        """
        child_item = Item(item_type, display_type, name, parent=self)
        self._children.append(child_item)
        child_item._parent = self
        logger.debug("Created %s" % child_item)
        return child_item

    @property
    def parent(self):
        """
        Parent Item object
        """
        return self._parent

    @property
    def children(self):
        """
        List of associated child items
        """
        return self._children

    @property
    def properties(self):
        """
        Access to a free form property bag where
        item data can be stored.
        """
        return self._properties

    @property
    def tasks(self):
        """
        Tasks associated with this item.
        """
        return self._tasks

    def add_task(self, task):
        """
        Adds a task to this item

        :param task: Task instance to be added
        """
        self._tasks.append(task)

    def _get_name(self):
        """
        The name of the item as a string.
        """
        return self._name

    def _set_name(self, name):
        # setter for name
        self._name = name

    name = property(_get_name, _set_name)

    def _get_type(self):
        """
        Item type as a string, typically following a hierarchical dot notation.
        For example, 'file', 'file.image', 'file.quicktime' or 'maya_scene'
        """
        return self._type

    def _set_type(self, item_type):
        # setter for type
        self._type = item_type

    type = property(_get_type, _set_type)

    def _get_display_type(self):
        """
        A human readable type string, suitable for UI and display purposes.
        """
        return self._display_type

    def _set_display_type(self, display_type):
        # setter for display_type
        self._display_type = display_type

    display_type = property(_get_display_type, _set_display_type)

    def _get_thumbnail_enabled(self):
        """
        Flag to indicate that thumbnails can be interacted with.
        - If ``True`, thumbnails will be visible and editable
          in the publish UI (via screen capture).
        - If ``False`` and a thumbnail has been set via the :meth:`thumbnail`
          property, the thumbnail will be visible but screen capture will
          be disabled.
        - If ``False`` and no thumbnail has been specified, no thumbnail will
          appear in the UI.
        """
        return self._thumbnail_enabled

    def _set_thumbnail_enabled(self, enabled):
        # setter for thumbnail_enabled
        self._thumbnail_enabled = enabled

    thumbnail_enabled = property(_get_thumbnail_enabled, _set_thumbnail_enabled)

    def _get_context(self):
        """
        The context associated with this item.
        If no context has been defined, the parent context
        will be returned or None if that hasn't been defined.
        """
        if self._context:
            return self._context
        elif self.parent:
            return self.parent.context
        else:
            return self._bundle.context

    def _set_context(self, context):
        # setter for context property
        self._context = context

    context = property(_get_context, _set_context)

    def _get_description(self):
        """
        Description of the item, description of the parent if not found
        or None if no description could be found.
        """
        if self._description:
            return self._description
        elif self.parent:
            return self.parent.description
        else:
            return None

    def _set_description(self, description):
        # setter for description property
        self._description = description

    description = property(_get_description, _set_description)

    def _get_thumbnail(self):
        """
        The associated thumbnail, as a QPixmap.
        The thumbnail is an image to represent the item visually
        such as a thumbnail of an image or a screenshot of a scene.

        If no thumbnail has been defined for this node, the parent
        thumbnail is returned, or None if no thumbnail exists.
        """
        if self._thumb_pixmap:
            return self._thumb_pixmap
        elif self.parent:
            return self.parent.thumbnail
        else:
            return None

    def _set_thumbnail(self, pixmap):
        self._thumb_pixmap = pixmap

    thumbnail = property(_get_thumbnail, _set_thumbnail)

    def _get_expanded(self):
        """
        Flag to indicate that this item's children should be expanded.
        """
        return self._expanded

    def _set_expanded(self, expand_state):
        # setter for expanded
        self._expanded = expand_state

    expanded = property(_get_expanded, _set_expanded)

    def _get_checked(self):
        """
        Flag to indicate that this item should be checked by default.

        Please note that the final state of the node is also affected by
        the child tasks. Below are some examples of how this interaction
        plays out in practice:

        - If all child tasks/items return ``checked: False`` in their accept
          method, the parent item will be unchecked, regardless
          of the state of this property.

        - If one or more child tasks return ``checked: True`` and the item
          checked state is False, the item and all its sub-items will be
          unchecked.
        """
        return self._checked

    def _set_checked(self, check_state):
        # setter for checked
        self._checked = check_state

    checked = property(_get_checked, _set_checked)

    def _get_enabled(self):
        """
        Flag to indicate that this item and its children should be enabled.
        """
        return self._enabled

    def _set_enabled(self, enabled):
        # setter for enabled
        self._enabled = enabled

    enabled = property(_get_enabled, _set_enabled)

    def set_thumbnail_from_path(self, path):
        """
        Helper method. Parses the contents of the given file path
        and tries to convert it into a QPixmap which is then
        used to set the thumbnail for the item.

        :param str path: Path to a file on disk
        """
        try:
            self._thumb_pixmap = QtGui.QPixmap(path)
        except Exception, e:
            logger.warning(
                "%r: Could not load '%s': %s" % (self, path, e)
            )

    def get_thumbnail_as_path(self):
        """
        Helper method. Writes the associated thumbnail to a temp file
        on disk and returns the path. This path is automatically deleted
        when the object goes out of scope.

        :returns: Path to a file on disk or None if no thumbnail set
        """
        if self.thumbnail is None:
            return None

        temp_path = tempfile.NamedTemporaryFile(
            suffix=".jpg",
            prefix="sgtk_thumb",
            delete=False
        ).name
        success = self.thumbnail.save(temp_path)

        if success:
            if os.path.getsize(temp_path) > 0:
                self._created_temp_files.append(temp_path)
            else:
                logger.debug(
                    "A zero-size thumbnail was written for %s, "
                    "no thumbnail will be uploaded." % self.name
                )
                return None
            return temp_path
        else:
            logger.warning(
                "Thumbnail save to disk failed. No thumbnail will be uploaded for %s." % self.name
            )
            return None

    @property
    def icon(self):
        """
        The associated icon, as a QPixmap.
        The icon is a small square image used to represent the item visually

        If no icon has been defined for this node, the parent
        icon is returned, or a default one if not defined
        """
        if self._icon_pixmap:
            return self._icon_pixmap
        elif self.parent:
            return self.parent.icon_pixmap
        else:
            # return default
            return QtGui.QPixmap(":/tk_multi_publish2/item.png")

    def set_icon_from_path(self, path):
        """
        Helper method. Parses the contents of the given file path
        and tries to convert it into a QPixmap which is then
        used to set the icon for the item.

        :param str path: Path to a file on disk
        """
        try:
            self._icon_pixmap = QtGui.QPixmap(path)
        except Exception, e:
            logger.warning(
                "%r: Could not load icon '%s': %s" % (self, path, e)
            )


