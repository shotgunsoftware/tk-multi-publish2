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


    def __init__(self, setting_name, data_type, default_value, description=None):
        self._name = setting_name
        self._type = data_type
        self._default_value = default_value
        self._value = default_value
        self._description = description or ""

    def set_value(self, value):
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def string_value(self):
        return str(self._value)

    @property
    def description(self):
        return self._description

    @property
    def default_value(self):
        return self._default_value

    @property
    def type(self):
        return self._type



