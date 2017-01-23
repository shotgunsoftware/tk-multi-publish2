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


    def __init__(self, setting_name, setting_params):
        self._name = setting_name
        self._params = setting_params

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._params.get("description") or ""

    @property
    def default_value(self):
        return self._params.get("default")

    @property
    def type(self):
        return self._params["type"]



