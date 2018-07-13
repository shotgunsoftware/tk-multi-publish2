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


class Setting(PublishData):
    """
    Holds configured settings for a task in a publish tree.
    """

    def __init__(self, name, data_type, default_value, description=None):
        """

        :param name:
        :param data_type:
        :param default_value:
        :param description:
        """

        super(Setting, self).__init__()

        self.default_value = default_value
        self.description = description
        self.name = name
        self.type = data_type
        self.value = default_value

    @property
    def string_value(self):
        """The setting value as a string."""
        return str(self.value)
