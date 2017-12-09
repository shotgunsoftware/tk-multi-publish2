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

class PublishPluginBase(sgtk.Hook):
    """
    The base class plugin used for all publish plugins. This class is inserted
    into any loaded publish plugin's class hierarchy by the publisher itself.

    The class implements the default UI state of publish plugins which shows
    only the description of the plugin. In order to customize the way all
    plugins are displayed when selected, you can modify this hook.

    To change the way an individual plugin is displayed in the UI, you can
    override these methods in that plugin. Alternatively, you can make a copy
    of this hook, configure the new file to be the base class for your plugin,
    and then make changes to the new file to display the plugin's UI in
    whatever way you want.
    """

    def create_settings_widget(self, parent):
        """
        Creates a Qt widget, for the supplied parent widget (a container widget
        on the right side of the publish UI).

        :param parent: The parent to use for the widget being created
        :return: A QtGui.QWidget or subclass that displays information about
            the plugin and/or editable widgets for modifying the plugin's
            settings.
        """

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

