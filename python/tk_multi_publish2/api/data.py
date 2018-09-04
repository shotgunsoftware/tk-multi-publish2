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

# here we import cPickle, if possible, otherwise pickle.
# see https://pymotw.com/2/pickle/#importing for more info
try:
    import cPickle as pickle
except:
    import pickle

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

        deserialized_dict = {}

        # iterate over the data and deserialize the values
        for (k, v) in data.iteritems():
            try:
                # ensure the serialized value is a string
                v = pickle.loads(str(v))
            except Exception, e:
                logger.error(
                    "Unable to deserialize value for data key: '%s'." % (k,)
                )
                raise
            deserialized_dict[k] = v

        return cls(**deserialized_dict)

    def __init__(self, **kwargs):
        """
        Initialize the data.

        This allows an instance to be created with supplied key/value pairs.
        """
        self.__dict__.update(**kwargs)

    def to_dict(self):
        """
        Returns a dictionary representation of the :class:`~PublishData`
        instance.

        Each item stored in the instance will be serialized.

        :return: A dictionary representing the data stored on the instance.
        """

        serialized_dict = {}

        # iterate over all data stored in the object and serialize it
        for (k, v) in self.__dict__.iteritems():
            try:
                v = pickle.dumps(v)
            except Exception, e:
                logger.error(
                    "Unable to serialize value for %s. key '%s', value '%s'." %
                    (self, k, v)
                )
                raise
            serialized_dict[k] = v

        return serialized_dict

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
