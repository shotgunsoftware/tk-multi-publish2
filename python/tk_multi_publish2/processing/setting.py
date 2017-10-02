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


class Setting(object):
    """
    A setting for a plugin or item
    """

    def __init__(self, setting_name, data_type, default_value, description=None, schema=None):
        """
        :param setting_name: The name of the setting
        :param data_type: The data type of the setting
        :param default_value: The setting's default value
        :param description: Description of the setting
        """
        self._name = setting_name
        self._type = data_type
        self._default_value = default_value
        self._value = default_value
        self._description = description or ""
        self._schema = schema

    @property
    def name(self):
        """
        The setting name
        """
        return self._name

    def _get_value(self):
        """
        The current value of the setting
        """
        return self._value

    def _set_value(self, value):
        # setter for value
        self._value = value

    value = property(_get_value, _set_value)

    @property
    def string_value(self):
        """
        The setting value, as a string
        """
        return str(self._value)

    @property
    def description(self):
        """
        The description of the setting
        """
        return self._description

    @property
    def default_value(self):
        """
        The default value of the setting.
        """
        return self._default_value

    @property
    def type(self):
        """
        The data type of the setting.
        """
        return self._type



