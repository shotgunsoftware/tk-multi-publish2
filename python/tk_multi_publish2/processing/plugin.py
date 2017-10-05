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
from sgtk.platform.qt import QtCore, QtGui
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

        # create an instance of the hook
        self._hook_instance = self._bundle.create_hook_instance(self._path)

        self._logger = logger
        self._settings = {}

        # kick things off
        self._validate_and_resolve_config()

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

    def _load_plugin_icon(self):
        """
        Loads the icon defined by the hook.

        :returns: QPixmap or None if not found
        """
        # load plugin icon
        pixmap = None
        try:
            icon_path = self._hook_instance.icon
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
            pixmap = QtGui.QPixmap(":/tk_multi_publish2/item.png")

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
    def icon(self):
        """
        The associated icon, as a pixmap, or None if no pixmap exists.
        """
        return self._icon_pixmap

    def run_accept(self, item):
        """
        Executes the hook accept method for the given item

        :param item: Item to analyze
        :returns: dictionary with boolean keys accepted/visible/enabled/checked
        """
        try:
            return self._hook_instance.accept(self.settings, item)
        except Exception, e:
            error_msg = traceback.format_exc()
            self._logger.error(
                "Error running accept for %s" % self,
                extra=_get_error_extra_info(error_msg)
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
        try:
            status = self._hook_instance.validate(settings, item)
        except Exception, e:
            error_msg = traceback.format_exc()
            self._logger.error(
                "Error Validating: %s" % (e,),
                extra=_get_error_extra_info(error_msg)
            )
            raise
        finally:
            # give qt a chance to do stuff
            QtCore.QCoreApplication.processEvents()

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
        try:
            self._hook_instance.publish(settings, item)
        except Exception, e:
            error_msg = traceback.format_exc()
            self._logger.error(
                "Error publishing: %s" % (e,),
                extra=_get_error_extra_info(error_msg)
            )
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
            self._hook_instance.finalize(settings, item)
        except Exception, e:
            error_msg = traceback.format_exc()
            self._logger.error(
                "Error finalizing: %s" % (e,),
                extra=_get_error_extra_info(error_msg)
            )
            raise
        finally:
            self._logger.info("Finalize complete!")
            # give qt a chance to do stuff
            QtCore.QCoreApplication.processEvents()


class CollectorPlugin(PluginBase):
    """
    Class that wraps around a collector hook

    Each collector object reflects an instance in the app configuration.
    """

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

