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

HookBaseClass = sgtk.get_hook_baseclass()


class CheckboxHandler(object):

    def __init__(self, layout, text):
        self._check_box = QtGui.QCheckBox(text)
        layout.addWidget(self._check_box)

        self._is_multi_edit_mode = None
        self._check_box.setTristate(False)

    @property
    def editor(self):
        return self._check_box

    def set_multi_edit_mode(self, is_multi_edit_mode):
        if self._is_multi_edit_mode == is_multi_edit_mode:
            return

        self._is_multi_edit_mode = is_multi_edit_mode
        self._check_box.setTristate(self._is_multi_edit_mode)
        if self._is_multi_edit_mode:
            self._check_box.setCheckState(QtCore.Qt.PartiallyChecked)

    def is_value_available(self):
        return self._check_box.checkState() != QtCore.Qt.PartiallyChecked

    @property
    def is_multi_edit_mode(self):
        return self._is_multi_edit_mode


class RowHandler(object):

    def __init__(self, layout, text, editor):
        self._layout = QtGui.QHBoxLayout()
        self._check_box = QtGui.QCheckBox(text)
        self._label = QtGui.QLabel(text)
        self._editor = editor

        # FIXME: Should take the size of the text + icon as the minimum width.
        self._check_box.setMinimumWidth(50)
        self._label.setMinimumWidth(50)

        self._check_box.stateChanged.connect(self._on_state_changed)

        self._layout.addWidget(self._check_box)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._editor)

        self._is_multi_edit_mode = None

        layout.addRow(self._layout)

    @property
    def editor(self):
        return self._editor

    def set_multi_edit_mode(self, is_multi_edit_mode):
        if self._is_multi_edit_mode == is_multi_edit_mode:
            return

        self._is_multi_edit_mode = is_multi_edit_mode
        self._check_box.setCheckState(QtCore.Qt.Unchecked)
        self._check_box.setVisible(is_multi_edit_mode is True)
        self._label.setVisible(is_multi_edit_mode is False)
        self._editor.setEnabled(is_multi_edit_mode is False)

    def _on_state_changed(self, state):
        self._editor.setEnabled(state == QtCore.Qt.Checked)

    def is_value_available(self):
        if not self._is_multi_edit_mode:
            return True
        else:
            return self._check_box.checkState() == QtCore.Qt.Checked


class CustomWidgetController(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QFormLayout(self)
        self.setLayout(layout)

        self.edit = RowHandler(layout, "Edit", QtGui.QLineEdit(self))
        self.number = RowHandler(layout, "Number", QtGui.QSpinBox(self))
        self.check_box = CheckboxHandler(layout, "Boolean")

        self.edit.editor.setFocus()
        self.number.editor.setMinimum(0)
        self.number.editor.setMaximum(100)


class PluginWithUi(HookBaseClass):
    """
    Plugin for creating generic publishes in Shotgun
    """

    def create_settings_widget(self, parent):
        """
        Creates a QT widget, parented below the given parent object, to
        provide viewing and editing capabilities for the given settings.

        :param parent: QWidget to parent the widget under
        :return: QWidget with an editor for the given setting or None if no custom widget is desired.
        """
        return CustomWidgetController(parent)

    def get_ui_settings(self, controller):
        """
        Returns the modified settings.
        """
        settings = {}
        if controller.edit.is_value_available():
            settings["edit"] = str(controller.edit.editor.text())

        if controller.number.is_value_available():
            settings["number"] = controller.number.editor.value()

        if controller.check_box.is_value_available():
            settings["boolean"] = (controller.check_box.editor.checkState() == QtCore.Qt.Checked)

        return settings

    def _requires_multi_edit_mode(self, tasks_settings, setting_name):
        """
        :returns: True if the setting is the same for every task, False otherwise.
        """
        return all(
            tasks_settings[0][setting_name] == task_setting[setting_name]
            for task_setting in tasks_settings
        ) is False

    def set_ui_settings(self, controller, tasks_settings):
        """
        Updates the UI with the list of settings.
        """
        controller.edit.set_multi_edit_mode(self._requires_multi_edit_mode(tasks_settings, "edit"))
        controller.edit.editor.setText(tasks_settings[0]["edit"])

        controller.number.set_multi_edit_mode(self._requires_multi_edit_mode(tasks_settings, "number"))
        controller.number.editor.setValue(tasks_settings[0]["number"])

        print tasks_settings[0]

        controller.check_box.set_multi_edit_mode(self._requires_multi_edit_mode(tasks_settings, "boolean"))
        if controller.check_box.is_multi_edit_mode is False:
            controller.check_box.editor.setCheckState(
                QtCore.Qt.Checked if tasks_settings[0]["boolean"] else QtCore.Qt.Unchecked
            )

    @property
    def name(self):
        """
        One line display name describing the plugin
        """
        return "This here has a UI."

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """
        return "This plugin has a UI"

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to recieve
        through the settings parameter in the accept, validate, publish and
        finalize methods.
        """
        return {
            "edit": {
                "type": "str",
                "default": "",
                "description": "First setting."
            },
            "number": {
                "type": "int",
                "default": "",
                "description": "Second setting."
            },
            "boolean": {
                "type": "bool",
                "default": "",
                "description": "Second setting."
            }
        }

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """
        return ["plugin.withui"]

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
        return {"accepted": True}

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
        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """
        self.logger.info("Plugin with UI data was published!")

    def finalize(self, settings, item):
        """
        Execute the finalization pass. This pass executes once
        all the publish tasks have completed, and can for example
        be used to version up files.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """
        pass
