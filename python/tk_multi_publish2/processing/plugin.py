# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from contextlib import contextmanager
import traceback

import sgtk
from .setting import Setting

logger = sgtk.platform.get_logger(__name__)

class PluginBase(object):
    """
    A base class for functionality common to plugin hooks (collectors and
    publish plugins).

    Each object reflects an instance in the app configuration.
    """

    def __init__(self, path, settings, logger):
        """
        :param path: Path to the collector hook
        :param settings: Dictionary of collector-specific settings
        :param logger: a logger object that will be used by the hook
        """

        # all plugins need a hook and a name
        self._path = path
        self._configured_settings = settings

        self._bundle = sgtk.platform.current_bundle()

        self._logger = logger
        self._settings = {}

        # create an instance of the hook
        self._hook_instance = self._create_hook_instance(self._path)

        # kick things off
        self._validate_and_resolve_config()

    def _create_hook_instance(self, path):
        """
        Create the plugin's hook instance. Subclasses can reimplement for more
        sophisticated hook instantiation.

        :param str path: The path to the hook file.
        :return: A hook instance
        """
        return self._bundle.create_hook_instance(path)

    def __repr__(self):
        """
        String representation
        """
        return "<%s %s>" % (self.__class__.__name__, self._path)

    def _validate_and_resolve_config(self):
        """
        Init helper method.

        Validates plugin settings and creates Setting objects
        that can be accessed from the settings property.
        """
        try:
            hook_settings_schema = self._hook_instance.settings
        except AttributeError, e:
            import traceback
            # property not defined by the hook
            logger.debug("no settings property defined by hook")
            hook_settings_schema = {}

        # Settings schema will be in the form:
        # "setting_a": {
        #     "type": "int",
        #     "default": 5,
        #     "description": "foo bar baz"
        # },

        for setting_name, setting_schema in hook_settings_schema.iteritems():

            # if the setting exists in the configured environment, grab that
            # value, validate it, and update the setting's value
            if setting_name in self._configured_settings:
                # this setting was provided by the config
                value = self._configured_settings[setting_name]
            else:
                # no value specified in the actual configuration
                value = setting_schema.get("default")

            # TODO: validate and resolve the configured setting

            setting = Setting(
                setting_name,
                data_type=setting_schema.get("type"),
                default_value=setting_schema.get("default"),
                description=setting_schema.get("description")
            )
            setting.value = value

            self._settings[setting_name] = setting

    @property
    def settings(self):
        """
        returns a dict of resolved raw settings given the current state
        """
        return self._settings


class PublishPlugin(PluginBase):
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

        self._tasks = []

        super(PublishPlugin, self).__init__(path, settings, logger)

        self._icon_pixmap = self._load_plugin_icon()

    def _create_hook_instance(self, path):
        """
        Create the plugin's hook instance.

        Injects the plugin base hook class in order to provide a default
        implementation.
        """
        return self._bundle.create_hook_instance(
            path,
            base_class=self._bundle.base_hooks.PublishPlugin
        )

    def _load_plugin_icon(self):
        """
        Loads the icon defined by the hook.

        :returns: QPixmap or None if not found
        """
        # TODO: this needs to be refactored. should be no UI stuff here
        from sgtk.platform.qt import QtGui

        # load plugin icon
        pixmap = None
        try:
            icon_path = self._hook_instance.icon
            if icon_path:
                try:
                    pixmap = QtGui.QPixmap(icon_path)
                except Exception, e:
                    self._logger.warning(
                        "%r: Could not load icon '%s': %s" % (self, icon_path, e)
                    )
        except AttributeError:
            # plugin does not have an icon
            pass

        # load default pixmap if hook doesn't define one
        if pixmap is None:
            pixmap = QtGui.QPixmap(":/tk_multi_publish2/task.png")

        return pixmap

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
            value = self._hook_instance.name
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
            value = self._hook_instance.description
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
            return self._hook_instance.item_filters
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
            hasattr(self._hook_instance, attr)
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
        # TODO: this needs to be refactored. should be no UI stuff here

        with self._handle_plugin_error(None, "Error laying out widgets: %s"):
            return self._hook_instance.create_settings_widget(parent)

    def run_get_ui_settings(self, parent):
        """
        Retrieves the settings from the custom UI.

        :param parent: Parent widget
        :type parent: :class:`QtGui.QWidget`
        """
        # TODO: this needs to be refactored. should be no UI stuff here

        with self._handle_plugin_error(None, "Error reading settings from UI: %s"):
            return self._hook_instance.get_ui_settings(parent)

    def run_set_ui_settings(self, parent, settings):
        """
        Provides a list of settings from the custom UI. It is the responsibility of the UI
        handle different values for the same setting.

        :param parent: Parent widget
        :type parent: :class:`QtGui.QWidget`

        :param settings: List of dictionary of settings as python literals.
        """
        # TODO: this needs to be refactored. should be no UI stuff here

        with self._handle_plugin_error(None, "Error writing settings to UI: %s"):
            self._hook_instance.set_ui_settings(parent, settings)

    def run_accept(self, item):
        """
        Executes the hook accept method for the given item

        :param item: Item to analyze
        :returns: dictionary with boolean keys accepted/visible/enabled/checked
        """
        try:
            return self._hook_instance.accept(self.settings, item)
        except Exception:
            error_msg = traceback.format_exc()
            self._logger.error(
                "Error running accept for %s" % self,
                extra = _get_error_extra_info(error_msg)
            )
            return {"accepted": False}
        finally:
            # give qt a chance to do stuff
            # TODO: this needs to be refactored. should be no UI stuff here
            from sgtk.platform.qt import QtCore
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
            status = self._hook_instance.validate(settings, item)

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
            self._hook_instance.publish(settings, item)

    def run_finalize(self, settings, item):
        """
        Executes the finalize logic for this plugin instance.

        :param settings: Dictionary of settings
        :param item: Item to analyze
        """
        with self._handle_plugin_error("Finalize complete!", "Error finalizing: %s"):
            self._hook_instance.finalize(settings, item)

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
                extra=_get_error_extra_info(exception_msg)
            )
            raise
        else:
            if success_msg:
                self._logger.info(success_msg)
        finally:
            # TODO: this needs to be refactored. should be no UI stuff here
            from sgtk.platform.qt import QtCore
            QtCore.QCoreApplication.processEvents()


class CollectorPlugin(PluginBase):
    """
    Class that wraps around a collector hook

    Each collector object reflects an instance in the app configuration.
    """

    def _create_hook_instance(self, path):
        """
        Create the plugin's hook instance.

        Injects the collector base hookclass in order to provide default
        implementation.
        """
        return self._bundle.create_hook_instance(
            path,
            base_class=self._bundle.base_hooks.CollectorPlugin
        )

    def run_process_current_session(self, item):
        """
        Executes the hook process_current_session method

        :param item: Item to parent collected items under.

        :returns: None (item creation handles parenting)
        """
        try:
            if hasattr(self._hook_instance.__class__, "settings"):
                # this hook has a 'settings' property defined. it is expecting
                # 'settings' to be passed to the processing method.
                return self._hook_instance.process_current_session(
                    self.settings, item)
            else:
                # the hook hasn't been updated to handle collector settings.
                # call the method without a settings argument
                return self._hook_instance.process_current_session(item)
        except Exception, e:
            error_msg = traceback.format_exc()
            logger.error(
                "Error running process_current_session for %s. %s" %
                (self, error_msg)
            )

    def run_process_file(self, item, path):
        """
        Executes the hook process_file method

        :param item: Item to parent collected items under.
        :param path: The path of the file to collect

        :returns: None (item creation handles parenting)
        """
        try:
            if hasattr(self._hook_instance.__class__, "settings"):
                # this hook has a 'settings' property defined. it is expecting
                # 'settings' to be passed to the processing method.
                return self._hook_instance.process_file(
                    self.settings, item, path)
            else:
                # the hook hasn't been updated to handle collector settings.
                # call the method without a settings argument
                return self._hook_instance.process_file(item, path)
        except Exception, e:
            error_msg = traceback.format_exc()
            logger.error(
                "Error running process_file for %s. %s" %
                (self, error_msg)
            )

def _get_error_extra_info(error_msg):
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

