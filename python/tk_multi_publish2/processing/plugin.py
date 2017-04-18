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
from sgtk.platform.qt import QtCore, QtGui
from .setting import Setting

logger = sgtk.platform.get_logger(__name__)


class Plugin(object):
    """
    Class that wraps around a publishing plugin hook

    Each plugin object reflects an instance in the
    app configuration.
    """

    def __init__(self, name, path, settings, logger):
        """
        :param name: Name to be used for this plugin instance
        :param path: Path to publish plugin hook
        :param settings: Dictionary of plugin-specific settings
        :param logger: a logger object that will be used by the hook
        """
        # all plugins need a hook and a name
        self._name = name
        self._path = path
        self._raw_config_settings = settings

        self._bundle = sgtk.platform.current_bundle()

        # create an instance of the hook
        self._plugin = self._bundle.create_hook_instance(self._path)

        self._configured_settings = {}
        self._required_runtime_settings = {}
        self._tasks = []
        self._logger = logger
        self._settings = {}

        # kick things off
        self._validate_and_resolve_config()
        self._icon_pixmap = self._load_plugin_icon()

    def __repr__(self):
        """
        String representation
        """
        return "<Publish Plugin %s>" % self._path

    def _load_plugin_icon(self):
        """
        Loads the icon defined by the hook.

        :returns: QPixmap or None if not found
        """
        # load plugin icon
        pixmap = None
        try:
            icon_path = self._plugin.icon
            try:
                pixmap = QtGui.QPixmap(icon_path)
            except Exception, e:
                logger.warning(
                    "%r: Could not load icon '%s': %s" % (self, icon_path, e)
                )
        except AttributeError:
            # plugin does not have an icon
            pass

        # load default pixmap if hook doesn't define one
        if pixmap is None:
            pixmap = QtGui.QPixmap(":/tk_multi_publish2/item.png")

        return pixmap

    def _validate_and_resolve_config(self):
        """
        Init helper method.

        Validates plugin settings and creates Setting objects
        that can be accessed from the settings property.
        """
        try:
            settings_defs = self._plugin.settings
        except AttributeError:
            # property not defined by the hook
            logger.debug("no settings property defined by hook")
            settings_defs = {}

        # "setting_a": {"type": "int", "default": 5, "description": "foo bar baz"},

        for settings_def_name, settings_def_params in settings_defs.iteritems():
            # todo - validate that the hook provides the relevant params

            setting = Setting(
                settings_def_name,
                data_type=settings_def_params["type"],
                default_value=settings_def_params["default"],
                description=settings_def_params["description"]
            )

            if settings_def_name in self._raw_config_settings:
                # this setting was provided by the config
                # todo - validate
                setting.value = self._raw_config_settings[settings_def_name]

            self._settings[settings_def_name] = setting

    @property
    def name(self):
        """
        The name of this plugin instance
        """
        return self._name

    @property
    def tasks(self):
        """
        Tasks associated with this publish plugin.
        """
        return self._tasks

    def add_task(self, task):
        """
        Adds a task to this publish plugin.

        :param task: Task instance to add.
        """
        self._tasks.append(task)

    @property
    def plugin_name(self):
        """
        The name of the publish plugin.
        Always a string.
        """
        value = None
        try:
            value = self._plugin.name
        except AttributeError:
            pass

        return value or "Untitled Integration."

    @property
    def description(self):
        """
        The decscription of the publish plugin.
        Always a string.
        """
        value = None
        try:
            value = self._plugin.description
        except AttributeError:
            pass

        return value or "No detailed description provided."

    @property
    def item_filters(self):
        """
        The item filters defined by this plugin
        or [] if none have been defined.
        """
        try:
            return self._plugin.item_filters
        except AttributeError:
            return []

    @property
    def icon(self):
        """
        The associated icon, as a pixmap, or None if no pixmap exists.
        """
        return self._icon_pixmap

    @property
    def settings(self):
        """
        returns a dict of resolved raw settings given the current state
        """
        return self._settings

    def run_accept(self, item):
        """
        Executes the hook accept method for the given item

        :param item: Item to analyze
        :returns: dictionary with boolean keys accepted/visible/enabled/checked
        """
        try:
            return self._plugin.accept(self.settings, item)
        except Exception, e:
            self._logger.exception("Error running accept for %s" % self)
            self._plugin.logger.error("Error running accept for %s" % self)
            return {"accepted": False}
        finally:
            # give qt a chance to do stuff
            QtCore.QCoreApplication.processEvents()

    def run_validate(self, settings, item):
        """
        Executes the validation logic for this plugin instance.

        :param settings: Dictionary of settings
        :param item: Item to analyze
        :return: True if validation passed, False otherwise.
        """
        status = False
        try:
            status = self._plugin.validate(settings, item)
        except Exception, e:
            self._logger.exception("Error Validating: %s" % e)
            raise
        finally:
            # give qt a chance to do stuff
            QtCore.QCoreApplication.processEvents()

        # check that we are not trying to publish to a project
        # (with no task set) or site level context
        if item.context.project is None or (item.context.entity is None and item.context.task is None):
            status = False
            self._logger.error("Please link '%s' to a Shotgun object and task!" % item.name)

        if status:
            self._logger.info("Validation successful!")
        else:
            self._logger.error("Validation failed.")

        return status

    def run_publish(self, settings, item):
        """
        Executes the publish logic for this plugin instance.

        :param settings: Dictionary of settings
        :param item: Item to analyze
        """
        try:
            self._plugin.publish(settings, item)
        except Exception, e:
            self._logger.exception("Error publishing: %s" % e)
            raise
        finally:
            self._logger.info("Publish complete!")
            # give qt a chance to do stuff
            QtCore.QCoreApplication.processEvents()

    def run_finalize(self, settings, item):
        """
        Executes the finalize logic for this plugin instance.

        :param settings: Dictionary of settings
        :param item: Item to analyze
        """
        try:
            self._plugin.finalize(settings, item)
        except Exception, e:
            self._logger.exception("Error finalizing: %s" % e)
            raise
        finally:
            self._logger.info("Finalize complete!")
            # give qt a chance to do stuff
            QtCore.QCoreApplication.processEvents()

