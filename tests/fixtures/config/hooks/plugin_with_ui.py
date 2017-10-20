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


class RowHandler(object):

    def __init__(self, layout, text, editor):
        self._is_multi_edit_mode = False
        self._layout = layout
        self._text = text
        self._editor = editor
        self._check_box = None
        self._index = layout.rowCount()

        self._field_layout = QtGui.QHBoxLayout()
        self._field_layout.addWidget(QtGui.QLabel(self._text))
        self._layout.addRow(self._field_layout, editor)

    @property
    def editor(self):
        return self._editor

    def set_multi_edit_mode(self, is_multi_edit_mode):
        if self._is_multi_edit_mode == is_multi_edit_mode:
            return
        self._is_multi_edit_mode = is_multi_edit_mode

        # Remove label and item.
        widget_item = self._layout.takeAt(self._index * 2)
        widget_item.widget().deleteLater()
        self._layout.takeAt(self._index * 2 + 1)

        if self._is_multi_edit_mode:
            self._check_box = QtGui.QCheckBox(self._text)
            self._check_box.setTristate(False)
            self._check_box.setChecked(QtCore.Qt.Unchecked)
            self._check_box.stateChanged.connect(self._on_state_changed)
            self._editor.setEnabled(False)
            self._layout.insertRow(self._index, self._check_box, self._editor)
        else:
            self._check_box = None
            self._layout.insertRow(self._index, self._text, self._editor)

    def _on_state_changed(self, state):
        self._editor.setEnabled(state == QtCore.Qt.Checked)

    def is_set(self):
        if not self._check_box:
            return True
        else:
            return self._check_box.checkState() == QtCore.Qt.Checked


class CustomWidgetController(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QFormLayout(self)
        self.setLayout(layout)

        self.edit = RowHandler(layout, "Edit", QtGui.QLineEdit(self))
        self.edit_2 = RowHandler(layout, "Edit2", QtGui.QLineEdit(self))

        self.edit.editor.setFocus()


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
        if controller.edit.is_set():
            settings["edit"] = str(controller.edit.editor.text())

        if controller.edit_2.is_set():
            settings["edit2"] = str(controller.edit_2.editor.text())

        return settings

    def _all_equal(self, tasks_settings, setting_name):
        """
        :returns: True if the setting is the same for every task, False otherwise.
        """
        return all(
            tasks_settings[0][setting_name] == task_setting[setting_name]
            for task_setting in tasks_settings
        )

    def set_ui_settings(self, controller, tasks_settings):
        """
        Updates the UI with the list of settings.
        """
        if self._all_equal(tasks_settings, "edit"):
            controller.edit.set_multi_edit_mode(False)
            controller.edit.editor.setText(tasks_settings[0]["edit"])
        else:
            controller.edit.set_multi_edit_mode(True)

        if self._all_equal(tasks_settings, "edit2"):
            controller.edit_2.set_multi_edit_mode(False)
            controller.edit_2.editor.setText(tasks_settings[0]["edit2"])
        else:
            controller.edit_2.set_multi_edit_mode(True)

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
            "edit2": {
                "type": "str",
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
