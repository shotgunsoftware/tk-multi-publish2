# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import abc
import pprint

import sgtk

from sgtk.platform.qt import QtCore, QtGui

HookBaseClass = sgtk.get_hook_baseclass()


################################################################################
# The following classes are a poor man's framework to have multi value editing
# widgets.


class WidgetHandlerBase(object):
    """
    Base class for widgets that can handle multiple values for a single setting.

    The multi edit mode is a mode where the widget will advertise that updating
    it will affect different tasks that have different values for a given
    setting. It is up to the derived class to decide how it wants to advertise
    that state.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, editor):
        """
        :param editor: Editing widget.
        """
        self._editor = editor
        self._is_multi_edit_mode = None

    @property
    def editor(self):
        """
        Returns the editing widget.
        """
        return self._editor

    @property
    def multi_edit_mode(self):
        """
        Flag indicating if the widget is in multi edit mode. Setting this to
        ``True`` will flip the widget into multi-edit mode.
        """
        return self._is_multi_edit_mode

    @multi_edit_mode.setter
    def multi_edit_mode(self, is_multi):
        if is_multi == self._is_multi_edit_mode:
            return

        self._is_multi_edit_mode = is_multi
        self._apply_edit_mode()

    @abc.abstractmethod
    def is_value_available(self):
        """
        Indicates if there is a value available to be consumed. This method
        generally returns True unless the widget is in multi-edit mode. In that
        """
        pass

    @abc.abstractmethod
    def _apply_edit_mode(self):
        pass


class CheckboxHandler(WidgetHandlerBase):
    """
    Handles a checkbox in multi-value and single-value scenarios.

    When there's multiple different values available for the checkbox, it will
    be displayed with a partially checked state.
    """

    def __init__(self, layout, text):
        """
        :param layout: Layout in witch to add the widget.
        :param text: Name of the setting.
        """
        super().__init__(QtGui.QCheckBox(text))
        layout.addWidget(self.editor)
        self.editor.setTristate(False)

    def _apply_edit_mode(self):
        """
        Updates the UI to indicate the widget has multiple values or not.
        """
        self.editor.setTristate(self.multi_edit_mode)
        # We're into multi-edit mode, so indicate the value is undetermined.
        if self.multi_edit_mode:
            self.editor.setCheckState(QtCore.Qt.PartiallyChecked)

    def is_value_available(self):
        """
        Indicates if a value is available to be consumed.
        """
        # If the checkbox is not partially checked, then the user has settled
        # on a value.
        return self.editor.checkState() != QtCore.Qt.PartiallyChecked


class WidgetHandler(WidgetHandlerBase):
    """
    Shows the editor widget with a label or checkbox depending on whether
    the widget is in multi-edit mode or not.

    When multiple values are available for this widget, the widget will by
    default be disabled and a checkbox will appear unchecked. By checking the
    checkbox, the user indicates they want to override the value with a specific
    one that will apply to all items.
    """

    def __init__(self, layout, text, editor):
        """
        :param layout: Layout to add the widget into.
        :param text: Text on the left of the editor widget.
        :param editor: Widget used to edit the value.
        """
        super().__init__(editor)

        self._layout = QtGui.QHBoxLayout()
        self._check_box = QtGui.QCheckBox(text)
        self._label = QtGui.QLabel(text)

        # FIXME: Should take the size of the text + icon as the minimum width.
        self._check_box.setMinimumWidth(50)
        self._label.setMinimumWidth(50)

        self._check_box.stateChanged.connect(self._on_state_changed)

        self._layout.addWidget(self._check_box)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self.editor)

        layout.addRow(self._layout)

    def _apply_edit_mode(self):
        """
        Updates the UI to indicate the widget has multiple values or not.
        """
        self._check_box.setCheckState(QtCore.Qt.Unchecked)
        # When the multi-edit mode is on we want to
        #  - show the check box
        #  - hide the label
        #  - disable the editor
        self._check_box.setVisible(self.multi_edit_mode is True)
        self._label.setVisible(self.multi_edit_mode is False)
        self._editor.setEnabled(self.multi_edit_mode is False)

    def _on_state_changed(self, state):
        """
        Called when the checkbox's state changes.
        """
        # Only allow the user to edit the value when the checkbox is checked.
        self.editor.setEnabled(state == QtCore.Qt.Checked)
        # If the widget is editable now, set focus to it so the user can edit
        # it right away.
        if self.editor.isEnabled():
            self.editor.setFocus()

    def is_value_available(self):
        """
        Indicates if a value is available to be consumed.
        """
        # If we're not in multi-edit mode, the value is available.
        if not self.multi_edit_mode:
            return True
        else:
            # If we are, then there's an updated value only if the
            # user actually checked the checkbox.
            return self._check_box.checkState() == QtCore.Qt.Checked


class CustomWidgetController(QtGui.QWidget):
    """
    This is the plugin's custom UI.
    """

    def __init__(self, parent, description_widget=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QFormLayout(self)
        self.setLayout(layout)

        self.edit = WidgetHandler(layout, "Edit", QtGui.QLineEdit(self))
        self.number = WidgetHandler(layout, "Number", QtGui.QSpinBox(self))
        self.check_box = CheckboxHandler(layout, "Boolean")

        self.edit.editor.setFocus()
        self.number.editor.setMinimum(0)
        self.number.editor.setMaximum(100)

        if description_widget:
            layout.addRow(description_widget)


class PluginWithUi(HookBaseClass):
    """
    Plugin for creating generic publishes in Shotgun
    """

    def create_settings_widget(self, parent, items):
        """
        Creates a QT widget, parented below the given parent object, to
        provide viewing and editing capabilities for the given settings.

        :param parent: QWidget to parent the widget under
        :return: QWidget with an editor for the given setting or None if no custom widget is desired.
        """
        return CustomWidgetController(
            parent,
            description_widget=super().create_settings_widget(parent, items),
        )

    def get_ui_settings(self, controller, items):
        """
        Returns the modified settings.
        """
        settings = {}
        if controller.edit.is_value_available():
            settings["edit"] = str(controller.edit.editor.text())

        if controller.number.is_value_available():
            settings["number"] = controller.number.editor.value()

        if controller.check_box.is_value_available():
            settings["boolean"] = (
                controller.check_box.editor.checkState() == QtCore.Qt.Checked
            )

        return settings

    def _requires_multi_edit_mode(self, tasks_settings, setting_name):
        """
        :returns: True if the setting is the same for every task, False otherwise.
        """
        return (
            all(
                tasks_settings[0][setting_name] == task_setting[setting_name]
                for task_setting in tasks_settings
            )
            is False
        )

    def set_ui_settings(self, controller, tasks_settings, items):
        """
        Updates the UI with the list of settings.
        """

        if len(tasks_settings) > 1 and not tasks_settings[0]["supports_multi_edit"]:
            raise NotImplementedError

        controller.edit.multi_edit_mode = self._requires_multi_edit_mode(
            tasks_settings, "edit"
        )
        controller.edit.editor.setText(tasks_settings[0]["edit"])

        controller.number.multi_edit_mode = self._requires_multi_edit_mode(
            tasks_settings, "number"
        )
        controller.number.editor.setValue(tasks_settings[0]["number"])

        controller.check_box.multi_edit_mode = self._requires_multi_edit_mode(
            tasks_settings, "boolean"
        )
        if controller.check_box.multi_edit_mode is False:
            controller.check_box.editor.setCheckState(
                QtCore.Qt.Checked
                if tasks_settings[0]["boolean"]
                else QtCore.Qt.Unchecked
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
        return "This plugin has a UI."

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to recieve
        through the settings parameter in the accept, validate, publish and
        finalize methods.
        """
        return {
            "edit": {"type": "str", "default": "", "description": "Text setting."},
            "number": {"type": "int", "default": "", "description": "Integer setting."},
            "boolean": {
                "type": "bool",
                "default": "",
                "description": "Boolean setting.",
            },
            "supports_multi_edit": {
                "type": "bool",
                "default": True,
                "description": (
                    "When set to False, the UI will advertise that it can't "
                    "handle multi-selection by raising a NotImplementedError."
                ),
            },
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
        print(item, "was published! The settings were:")
        pprint.pprint(dict(list((k, v.value) for k, v in settings.items())))
        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """
        pass

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
