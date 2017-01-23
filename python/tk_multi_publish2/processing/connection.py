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


class Connection(object):

    def __init__(self):
        pass

    @property
    def phase(self):
        raise NotImplementedError

    def evaluate(self, item):
        raise NotImplementedError


class StaticValue(Connection):

    def __init__(self, value):
        super(StaticValue, self).__init__()
        self._value = value
        self._bundle = sgtk.platform.current_bundle()

    def __repr__(self):
        return "<Static value %s>" % self._value

    @property
    def phase(self):
        # static values are valid in both validate and publish phases
        return self._bundle.VALIDATE

    def evaluate(self, item):
        return self._value


class PluginOutput(Connection):

    def __init__(self, name, manifest, plugin):
        super(PluginOutput, self).__init__()
        self._name = name
        self._manifest = manifest
        self._plugin = plugin

    def __repr__(self):
        return "<Plugin %r output %s (type %s, phase %s)>" % (
            self._plugin,
            self._name,
            self.type,
            self.phase
        )

    @property
    def type(self):
        return self._manifest["type"]

    @property
    def phase(self):
        return self._manifest["phase"]

    def evaluate(self, item):
        # add debug
        return self._plugin.get_output_value(self._name, item)

