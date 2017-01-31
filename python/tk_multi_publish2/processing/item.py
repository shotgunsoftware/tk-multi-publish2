# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

logger = sgtk.platform.get_logger(__name__)

from sgtk.platform.qt import QtCore, QtGui

class Item(object):
    """
    An object representing an item that should be processed
    """

    def __init__(self, type, display_type, display_name, parent):
        self._name = display_name
        self._type = type
        self._display_type = display_type
        self._parent = parent
        self._thumb_pixmap = None
        self._children = []
        self._tasks = []
        self._properties = {}
        self._parent = None
        self._icon_path = None

    def __repr__(self):
        if self._parent:
            return "<Item %s|%s:%s>" % (self._parent, self._type, self._name)
        else:
            return "<Item %s:%s>" % (self._type, self._name)

    def create_item(self, item_type, display_type, display_name):
        """
        Create a new item
        """
        child_item = Item(item_type, display_type, display_name, parent=self)
        self._children.append(child_item)
        child_item._parent = self
        logger.debug("Created %s" % child_item)
        return child_item

    def set_thumbnail(self, path):
        try:
            self._thumb_pixmap = QtGui.QPixmap(path)
        except Exception, e:
            self._thumb_pixmap = None
            logger.warning(
                "%r: Could not load icon '%s': %s" % (self, path, e)
            )

    def set_thumbnail_pixmap(self, pixmap):
        self._thumb_pixmap = pixmap

    def set_icon(self, path):
        self._icon_path = path

    @property
    def icon_pixmap(self):
        if self._icon_path:
            try:
                pixmap = QtGui.QPixmap(self._icon_path)
                return pixmap
            except Exception, e:
                logger.warning(
                    "%r: Could not load thumbnail '%s': %s" % (self, self._icon_path, e)
                )
        elif self.parent:
            return self.parent.icon_pixmap
        else:
            return None

    @property
    def thumbnail_pixmap(self):
        """
        Return parent thumb if nothing else found
        """
        if self._thumb_pixmap:
            return self._thumb_pixmap
        elif self.parent:
            return self.parent.thumbnail_pixmap
        else:
            return None

    @property
    def children(self):
        return self._children

    @property
    def name(self):
        return self._name

    @property
    def display_type(self):
        return self._display_type

    @property
    def type(self):
        return self._type

    @property
    def parent(self):
        return self._parent

    @property
    def properties(self):
        return self._properties

    @property
    def tasks(self):
        return self._tasks

    def add_task(self, task):
        self._tasks.append(task)
