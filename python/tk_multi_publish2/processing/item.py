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


class Item(object):
    """
    An object representing an item that should be processed
    """

    def __init__(self, type, name, parent=None):
        self._name = name
        self._type = type
        self._parent = parent
        self._properties = {}

    def __repr__(self):
        if self._parent:
            return "<Item %s|%s:%s>" % (self._parent, self._type, self._name)
        else:
            return "<Item %s:%s>" % (self._type, self._name)

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def parent(self):
        return self._parent

    @property
    def properties(self):
        return self._properties

