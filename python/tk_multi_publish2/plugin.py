# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import re
import sgtk
import collections

from sgtk.platform.qt import QtCore, QtGui

logger = sgtk.platform.get_logger(__name__)

from .errors import PluginValidationError, PluginNotFoundError, ValidationFailure, PublishFailure
from sgtk import TankError

REFERENCE_TOKEN_REGEX = "^{([^}^{]*)}$"

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



class Plugin(object):

    def __init__(self, config, plugin_manager):

        self._plugin_manager = plugin_manager

        # publish_plugins:
        # - name: snapshot_maya_scene_2
        #   hook: "{self}/maya/snapshot.py"
        #   settings:
        #     name: foo
        #     write_timestamp: true
        #   inputs:
        #     input_a: {snapshot_maya_scene.output_a}
        #     input_b: 14


        # all plugins need a hook and a name
        self._path = config["hook"]
        self._name = config["name"]

        # the raw data from the config
        self._raw_config_inputs = config.get("inputs") or {}
        self._raw_config_settings = config.get("settings") or {}

        # resolved config settings
        self._configured_settings = {}
        self._required_runtime_settings = {}
        self._inputs = {}
        self._outputs_per_item = collections.defaultdict(dict)

        self._bundle = sgtk.platform.current_bundle()
        self._scan_scene_data = {}

        # init the plugin
        self._plugin = self._bundle.execute_hook_expression(self._path, "get_instance")

        # read in the output definitions that this plugin exposes
        #
        # {
        #   "output_a": {"type": "int", "description": "foo bar baz", "phase": self.parent.VALIDATE}
        # }
        #
        try:
            # todo - validate and make sure that all fields are present for all records
            self._output_defs = self._plugin.outputs
        except AttributeError:
            # property not defined by the hook
            logger.debug("no outputs property defined by hook")
            self._output_defs = {}

    def __repr__(self):
        return "<Publish Plugin %s @ %s>" % (self._name, self._path)

    def __str__(self):
        return "Publish Plugin %s" % self._name

    def validate_and_resolve_config(self):
        """
        Validate all values. Resolve links
        """

        # validate configuration

        # first check that which settings are provided from the config.
        # the manifest in a hook looks like this:
        #
        # def settings(self):
        #     settings = {}
        #     settings["setting_a"] = {"type": "int", "default": 5, "description": "foo bar baz"}
        #     settings["setting_b"] = {"type": "bool", "default": True, "description": "Should we do stuff?"}
        #     return inputs
        #
        # and in the env config
        #   settings:
        #     name: foo
        #     write_timestamp: true
        #
        # note: values that are defined in the settings manifest for the plugin
        #       but not in the config will be required via the
        #       required_runtime_settings mechanism

        try:
            settings_defs = self._plugin.settings
        except AttributeError:
            # property not defined by the hook
            logger.debug("no settings property defined by hook")
            settings_defs = {}

        for settings_def_name, settings_def_params in settings_defs.iteritems():
            # todo - validate that the hook provides the relevant params
            if settings_def_name in self._raw_config_settings:
                # this setting was provided by the config
                # todo - validate
                self._configured_settings[settings_def_name] = self._raw_config_settings[settings_def_name]
            else:
                # this setting needs to be pulled from the UI
                # todo - ensure all keys are set
                self._required_runtime_settings[settings_def_name] = settings_def_params


        # validate inputs to make sure they connect to a valid output
        #
        # @property
        # def inputs(self):
        #     inputs = {}
        #     inputs["input_a"] = {"type": "int", "description": "foo bar baz", "phase": self.parent.VALIDATE}
        #     inputs["input_b"] = {"type": "int", "description": "foo bar baz", "phase": self.parent.VALIDATE}
        #     return inputs
        #
        # and in the env config
        #   inputs:
        #     input_a: {snapshot_maya_scene.output_a}
        #     input_b: 14
        #


        try:
            input_defs = self._plugin.inputs
        except AttributeError:
            # property not defined by the hook
            logger.debug("no inputs property defined by hook")
            input_defs = {}

        for input_def, input_def_params in input_defs.iteritems():
            if input_def not in self._raw_config_inputs:
                raise PluginValidationError("%s: Cannot find configuration for input '%s'" % (self, input_def))

            # check if the config value is a reference
            if re.search(REFERENCE_TOKEN_REGEX, str(self._raw_config_inputs[input_def])):
                # value is a reference
                # resolve it against an output
                logger.debug("resolve reference %s" % self._raw_config_inputs[input_def])
                value = re.search(
                    REFERENCE_TOKEN_REGEX,
                    str(self._raw_config_inputs[input_def])
                ).group(1)
                if len(value.split(".")) != 2:
                    raise PluginValidationError("%s: invalid syntax '{%s}'" % (self, value))
                (source_plugin_name, output_name) = value.split(".")

                # now find source plugin
                try:
                    source_plugin = self._plugin_manager.get_plugin(source_plugin_name)
                except PluginNotFoundError:
                    raise PluginValidationError("%s: referenced plugin '{%s}' does not exist!" % (self, value))

                output = source_plugin._get_output(output_name)
                # {"type": "int", "description": "foo bar baz", "phase": self.parent.VALIDATE}

                # check that input and output is same type
                if output.type != input_def_params["type"]:
                    raise PluginValidationError(
                        "%s: type mismatch between %s (type %s) and %s (%s)" % (
                            self,
                            input_def,
                            input_def_params["type"],
                            value,
                            output.type
                        )
                    )

                # check that phase is valid
                if input_def_params["phase"] == self._bundle.VALIDATE and output.phase == self._bundle.PUBLISH:
                    raise PluginValidationError(
                        "%s: %s is connected to %s but the output data is generated in the publish "
                        "phase and input is required at the validate phase" % (self, input_def, value)
                    )

                # all good!
                self._inputs[input_def] = output

            else:
                # value is a value
                # todo - validate
                self._inputs[input_def] = StaticValue(self._raw_config_inputs[input_def])

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        try:
            return self._plugin.description_html
        except AttributeError:
            return "No detailed description provided."

    @property
    def title(self):
        try:
            return self._plugin.title
        except AttributeError:
            return "Untitled Integration."

    @property
    def summary(self):
        try:
            return self._plugin.summary
        except AttributeError:
            return ""

    @property
    def icon_pixmap(self):
        try:
            icon_path = self._plugin.icon
            try:
                pixmap = QtGui.QPixmap(icon_path)
                return pixmap
            except Exception, e:
                logger.warning(
                    "%r: Could not load icon '%s': %s" % (self, icon_path, e)
                )
        except AttributeError:
            return None

    @property
    def required_settings(self):
        """
        Settings required to be specified by a UI or external process
        {
            "version_number": {"type": "int", "default": 5, "description": "foo bar baz"}
        }
        """
        settings = []
        for (setting_name, setting_params) in self._required_runtime_settings.iteritems():
            settings.append(Setting(setting_name, setting_params))
        return settings


    def _get_output(self, name):
        """
        Return the output parameter definitions
        {
          "output_a": {"type": "int", "description": "foo bar baz", "phase": self.parent.VALIDATE}
        }
        """
        if name in self._output_defs:
            return PluginOutput(name, self._output_defs[name], self)

        raise PluginNotFoundError(
            "%s: Plugin output %s not found! Available outputs are %s" % (
                self,
                name,
                ", ".join(self._output_defs.keys())
            )
        )

    def get_output_value(self, name, item):

        # todo - raise
        if item in self._outputs_per_item:
            # we got a item-item match
            return self._outputs_per_item[item][name]

        elif len(self._outputs_per_item) == 1:
            # this node only has got a single item
            return self._outputs_per_item[self._outputs_per_item.keys()[0]][name]

        else:
            # this node has multiple items but not named to match our item
            logger.warning("cannot match up item. picking first") # todo <-- improve
            return self._outputs_per_item[self._outputs_per_item.keys()[0]][name]

    def scan_scene(self, log, runtime_settings):

        # get the full settings merged together
        full_settings = runtime_settings.copy()
        full_settings.update(self._configured_settings)

        self._scan_scene_data = self._plugin.scan_scene(
            log,
            full_settings
        )

        return self._scan_scene_data.keys()

    def validate(self, log, item, runtime_settings):

        # get the full settings merged together
        full_settings = runtime_settings.copy()
        full_settings.update(self._configured_settings)

        # evaluate all input values
        evaluated_inputs = {}
        for input_name, connection in self._inputs.iteritems():
            # we cannot evaluate publish time connections at this stage
            if connection.phase == self._bundle.VALIDATE:
                evaluated_inputs[input_name] = connection.evaluate(item)

        try:
            output_data = self._plugin.validate(
                log,
                item,
                full_settings,
                evaluated_inputs
            )
            if output_data:
                self._outputs_per_item[item].update(output_data)

        except TankError, e:
            raise ValidationFailure("Validation failed for %r: %s" % (self, e))

        # todo - evaluate that all outputs were returned

    def publish(self, log, item, runtime_settings):

        # get the full settings merged together
        full_settings = runtime_settings.copy()
        full_settings.update(self._configured_settings)

        # evaluate all input values
        evaluated_inputs = {}
        for input_name, connection in self._inputs.iteritems():
            evaluated_inputs[input_name] = connection.evaluate(item)

        try:
            output_data = self._plugin.publish(
                log,
                item,
                full_settings,
                evaluated_inputs
            )
            if output_data:
                self._outputs_per_item[item].update(output_data)

        except TankError, e:
            raise PublishFailure("Publish failed for %r: %s" % (self, e))

        # todo - evaluate that all outputs were returned
