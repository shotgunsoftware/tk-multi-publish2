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
import sgtk
import copy

logger = sgtk.platform.get_logger(__name__)


class PublishData(collections.MutableMapping):
    """
    A simple dictionary-like object for storing/serializing arbitrary publish
    data.

    Provides access via standard dict syntax as well as dot notation. This is
    used as the base class for any arbitrary data exposed by the publish API
    including internal representation of settings (as configured or modified
    by the UI) and publish item properties.
    """

    @classmethod
    def from_dict(cls, data):
        """
        Create a :class:`~PublishData` instance from a dict.

        This method is used to deserialize data returned by :meth:`to_dict`.

        :param data: A dictionary of instance data, as returned by
            :meth:`to_dict`.

        :return: A :class:`~PublishData` instance.
        """
        return cls(**data)

    def _from_json(self, data):
        if isinstance(data, dict):
            if "__tk_type" in data:
                if data["__tk_type"] == "sgtk.Template":
                    return self.parent.sgtk.templates[data["name"]]
                raise NotImplementedError("Serialized type %s is not supported" % data["__tk_type"])
            else:
                return {k: self._from_json(data[k]) for k in data}
        elif isinstance(data, list):
            return [self._from_json(d) for d in data]
        else:
            return d

    def __init__(self, **kwargs):
        """
        .. note:: Developers should not create instances of this class. Instances
            of ``PublishData`` are exposed via properties and settings of other
            classes.
        """
        self.__dict__.update(**kwargs)

    def to_dict(self):
        """
        Returns a dictionary representation of the :class:`~PublishData`
        instance.

        Each item stored in the instance will be serialized.

        :return: A dictionary representing the data stored on the instance.
        """
        return copy.deepcopy(self._make_json_serializable(self.__dict__))

    def _make_json_serializable(self, data):
        if isinstance(data, dict):
            return {
                k: self._make_json_serializable(data[k]) for k in data
            }
        elif isinstance(data, list):
            return [self._make_json_serializable(d) for d in data]
        elif isinstance(data, sgtk.Template):
            return {
                "__tk_type": "sgtk.Template",
                "name": data.name
            }
        else:
            return data

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
