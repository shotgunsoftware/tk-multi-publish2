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


class PublishPlugin(sgtk.Hook):
    """
    The base class is used for all publish plugins. This class is inserted
    into any loaded publish plugin's class hierarchy by the publisher itself.

    The class implements the default UI state of publish plugins which shows
    only the description of the plugin. It also provides the official API and
    documentation for publish plugins.
    """

    ############################################################################
    # Plugin properties

    @property
    def icon(self):
        """
        The path to an icon on disk that is representative of this plugin.
        """
        raise NotImplementedError

    @property
    def name(self):
        """
        The name of this plugin.
        """
        raise NotImplementedError

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting for display in the UI.
        """
        raise NotImplementedError

    @property
    def settings(self):
        """
        A dictionary defining the settings that this plugin expects to receive
        through the settings parameter in the accept, validate, publish and
        finalize methods.

        A dictionary on the following form::

            {
                "Publish Template": {
                    "type": "template",
                    "default": None,
                    "description": "A template required to publish the file."
            }

        The type string should be one of the data types that toolkit accepts
        as part of its environment configuration.

        The settings are exposed via the `publish_plugins` setting in the
        app's configuration. Example::

            - name: Publish to Shotgun
              hook: "{config}/my_publish_plugin.py"
              settings:
                Publish Template: my_publish_template
        """
        return {}

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        As items are collected by the collector hook, they are given an item
        type string. The strings provided by this property will be matched
        against each item's item type.

        Only items with item types matching entries in this list will be
        presented to the accept() method. Strings can contain glob patters such
        as *, for example ["maya.*", "file.maya"]
        """
        raise NotImplementedError

    ############################################################################
    # Publish processing methods

    def accept(self, settings, item):
        """
        Method called by the publisher to determine if an item is of any
        interest to this plugin. Only items matching the filters defined via the
        item_filters property will be presented to this method.

        A publish task will be generated for each item accepted here. Returns a
        dictionary with the following booleans:

            - accepted: Indicates if the plugin is interested in this value at
                all. Required.
            - enabled: If True, the plugin will be enabled in the UI, otherwise
                it will be disabled. Optional, True by default.
            - visible: If True, the plugin will be visible in the UI, otherwise
                it will be hidden. Optional, True by default.
            - checked: If True, the plugin will be checked in the UI, otherwise
                it will be unchecked. Optional, True by default.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process

        :returns: dictionary with boolean keys accepted, required and enabled
        """
        raise NotImplementedError

    def validate(self, settings, item):
        """
        Validates the given item to check that it is ok to publish.

        Returns a boolean to indicate validity.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process

        :returns: True if item is valid, False otherwise.
        """
        raise NotImplementedError

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """
        raise NotImplementedError

    def finalize(self, settings, item):
        """
        Execute the finalization pass. This pass executes once all the publish
        tasks have completed, and can for example be used to version up files.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """
        raise NotImplementedError

    ############################################################################
    # Methods for creating/displaying custom plugin interface

    # NOTE: We provide a default settings widget implementation here to show the
    # plugin's description. This allows for a consistent default look and
    # allows clients to write their own publish plugins while deferring custom
    # UI settings implementations until needed.

    def create_settings_widget(self, parent):
        """
        Creates a Qt widget, for the supplied parent widget (a container widget
        on the right side of the publish UI).

        :param parent: The parent to use for the widget being created
        :return: A QtGui.QWidget or subclass that displays information about
            the plugin and/or editable widgets for modifying the plugin's
            settings.
        """

        # defer Qt-related imports
        from sgtk.platform.qt import QtCore, QtGui

        # create a group box to display the description
        description_group_box = QtGui.QGroupBox(parent)
        description_group_box.setTitle("Description:")

        # The publish plugin that subclasses this will implement the
        # `description` property. We'll use that here to display the plugin's
        # description in a label.
        description_label = QtGui.QLabel(self.description)
        description_label.setWordWrap(True)

        # create the layout to use within the group box
        description_layout = QtGui.QVBoxLayout()
        description_layout.addWidget(description_label)
        description_layout.addStretch()
        description_group_box.setLayout(description_layout)

        # return the description group box as the widget to display
        return description_group_box

    def get_ui_settings(self, widget):
        """
        Invoked by the publisher when the selection changes so the new settings
        can be applied on the previously selected tasks.

        The widget argument is the widget that was previously created by
        `create_settings_widget`.

        The method returns an dictionary, where the key is the name of a
        setting that should be updated and the value is the new value of that
        setting. Note that it is not necessary to return all the values from
        the UI. This is to allow the publisher to update a subset of settings
        when multiple tasks have been selected.

        Example::

            {
                 "setting_a": "/path/to/a/file"
            }

        :param widget: The widget that was created by `create_settings_widget`
        """

        # the default implementation does not show any editable widgets, so this
        # is a no-op. this method is required to be defined in order for the
        # custom UI to show up in the app
        return {}

    def set_ui_settings(self, widget, settings):
        """
        Allows the custom UI to populate its fields with the settings from the
        currently selected tasks.

        The widget is the widget created and returned by
        `create_settings_widget`.

        A list of settings dictionaries are supplied representing the current
        values of the settings for selected tasks. The settings dictionaries
        correspond to the dictionaries returned by the settings property of the
        hook.

        Example::

            settings = [
            {
                 "seeting_a": "/path/to/a/file"
                 "setting_b": False
            },
            {
                 "setting_a": "/path/to/a/file"
                 "setting_b": False
            }]

        The default values for the settings will be the ones specified in the
        environment file. Each task has its own copy of the settings.

        When invoked with multiple settings dictionaries, it is the
        responsibility of the custom UI to decide how to display the
        information. If you do not wish to implement the editing of multiple
        tasks at the same time, you can raise a `NotImplementedError` when
        there is more than one item in the list and the publisher will inform
        the user than only one task of that type can be edited at a time.

        :param widget: The widget that was created by `create_settings_widget`
        :param settings: a list of dictionaries of settings for each selected
            task.
        """

        # the default implementation does not show any editable widgets, so this
        # is a no-op. this method is required to be defined in order for the
        # custom UI to show up in the app
        pass

