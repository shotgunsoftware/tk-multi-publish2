# Copyright (c) 2018 Shotgun Software Inc.
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

    Provides access via standard dict syntax as well as dot notation. This is
    used as the base class for any arbitrary data exposed by the publish API
    including internal representation of settings (as configured or modified
    by the UI) and publish item properties.
    """

    @classmethod
    def clone(cls, pub_data_obj):
        """
        Returns a new :class:`~.PublishData`` instance with a deep copy of the
        data for the supplied object.
        """
        return cls(**pub_data_obj.to_dict())

    def __init__(self, **kwargs):
        """
        Initialize the data. This allows an instance to be created with supplied
        key/value pairs.
        """
        self.__dict__.update(**kwargs)

    def to_dict(self):
        return self.__dict__

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