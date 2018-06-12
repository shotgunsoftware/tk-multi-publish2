# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import collections


class PublishData(collections.MutableMapping):
    """
    A simple dictionary-like object for storing arbitrary data.

    Provides access via standard dict syntax as well as dot notation.
    """

    def __init__(self, **kwargs):
        """
        Initialize the data. This allows an instance to be created with supplied
        key/value pairs.
        """
        self.__dict__.update(**kwargs)

    def deep_copy(self):
        """
        Returns a new ``PublishData`` instance with a deep copy of the data
        defined by the current instance.
        """
        return PublishData(**self.to_dict())

    def to_dict(self):
        """
        Returns a regular dict representation of the object.
        """
        object_dict = {}
        for (key, value) in self.items():
            object_dict[key] = value

        return object_dict

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)