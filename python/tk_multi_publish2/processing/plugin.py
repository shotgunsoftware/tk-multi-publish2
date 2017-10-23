# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import traceback
import sgtk
from contextlib import contextmanager
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
    def has_custom_ui(self):
        """
        Checks if a plugin has a custom widget.

        :returns: ``True`` if the plugin supports ``create_settings_widget``,
            ``get_ui_settings`` and ``set_ui_settings``,``False`` otherwise.
        """
        return all(
            hasattr(self._plugin, attr)
            for attr in ["create_settings_widget", "get_ui_settings", "set_ui_settings"]
        )

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

    def run_create_settings_widget(self, parent):
        """
        Creates a custom widget to edit a plugin's settings.

        :param parent: Parent widget
        :type parent: :class:`QtGui.QWidget`
        """
        with self._handle_plugin_error(None, "Error laying out widgets: %s"):
            return self._plugin.create_settings_widget(parent)

    def run_get_ui_settings(self, parent):
        """
        Retrieves the settings from the custom UI.

        :param parent: Parent widget
        :type parent: :class:`QtGui.QWidget`
        """
        with self._handle_plugin_error(None, "Error reading settings from UI: %s"):
            return self._plugin.get_ui_settings(parent)

    def run_set_ui_settings(self, parent, settings):
        """
        Provides a list of settings from the custom UI. It is the responsibility of the UI
        handle different values for the same setting.

        :param parent: Parent widget
        :type parent: :class:`QtGui.QWidget`

        :param settings: List of dictionary of settings as python literals.
        """
        with self._handle_plugin_error(None, "Error writing settings to UI: %s"):
            self._plugin.set_ui_settings(parent, settings)

    def run_accept(self, item):
        """
        Executes the hook accept method for the given item

        :param item: Item to analyze
        :returns: dictionary with boolean keys accepted/visible/enabled/checked
        """
        try:
            return self._plugin.accept(self.settings, item)
        except Exception:
            error_msg = traceback.format_exc()
            self._logger.error(
                "Error running accept for %s" % self,
                extra=self._get_error_extra_info(error_msg)
            )
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
        with self._handle_plugin_error(None, "Error Validating: %s"):
            status = self._plugin.validate(settings, item)

        # check that we are not trying to publish to a site level context
        if item.context.project is None:
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
        with self._handle_plugin_error("Publish complete!", "Error publishing: %s"):
            self._plugin.publish(settings, item)

    def run_finalize(self, settings, item):
        """
        Executes the finalize logic for this plugin instance.

        :param settings: Dictionary of settings
        :param item: Item to analyze
        """
        with self._handle_plugin_error("Finalize complete!", "Error finalizing: %s"):
            self._plugin.finalize(settings, item)

    @contextmanager
    def _handle_plugin_error(self, success_msg, error_msg):
        """
        Creates a scope that will properly handle any error raised by the plugin
        while the scope is executed.

        .. note::
            Any exception raised by the plugin is bubbled up to the caller.

        :param str success_msg: Message to be displayed if there is no error.
        :param str error_msg: Message to be displayed if there is an error.
        """

        try:
            # Execute's the code inside the with statement. Any errors will be
            # caught and logged and the events will be processed
            yield
        except Exception as e:
            exception_msg = traceback.format_exc()
            self._logger.error(
                error_msg % (e,),
                extra=self._get_error_extra_info(exception_msg)
            )
            raise
        else:
            if success_msg:
                self._logger.info(success_msg)
        finally:
            QtCore.QCoreApplication.processEvents()

    def _get_error_extra_info(self, error_msg):
        """
        A little wrapper to return a dictionary of data to show a button in the
        publisher with the supplied error message.

        :param error_msg: The error message to display.
        :return: An logging "extra" dictionary to show the error message.
        """

        return {
            "action_show_more_info": {
                "label": "Error Details",
                "tooltip": "Show the full error tack trace",
                "text": "<pre>%s</pre>" % (error_msg,)
            }
        }
