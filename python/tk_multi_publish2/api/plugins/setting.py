# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from ..data import PublishData


class PluginSetting(PublishData):
    """
    This class provides an interface to settings defined for a given
    :ref:`publish-api-task`.
    """

    def __init__(self, name, data_type, default_value, description=None):
        """
        This class derives from :ref:`publish-api-data`.  A few special keys
        are set by default and are accessible after initialization. Those keys
        are:

        * ``default_value``: The default value as configured for this setting.
        * ``description``: Any description provided for this setting in the config.
        * ``name``: The display name for this setting.
        * ``type``: The type for this setting (:py:attr:`bool`, :py:attr:`str`, etc).
        * ``value``: The current value of this setting.

        .. note:: There is typically no need to create instances of this class
            manually. Each :ref:`publish-api-task` will expose a dictionary of
            configured ``PluginSettings``.
        """

        super().__init__()

        self.default_value = default_value
        self.description = description
        self.name = name
        self.type = data_type
        self.value = default_value

    @property
    def string_value(self):
        """The setting value as a string."""
        return str(self.value)
