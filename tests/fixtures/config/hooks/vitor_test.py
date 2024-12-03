# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import pprint
import sgtk

from sgtk.platform.qt import QtGui

HookBaseClass = sgtk.get_hook_baseclass()


class VitorPlugin(HookBaseClass):
    """
    Vitor, a client, was having issues with the UI. Adding this case here to
    ensure that it works and for future reference.
    """

    def create_settings_widget(self, parent):

        qtwidgets = self.load_framework("tk-framework-qtwidgets_v2.x.x")

        return CustomNameWidget(
            parent,
            qtwidgets,
            description_widget=super().create_settings_widget(parent),
        )

    def get_ui_settings(self, widget):

        settings = {}
        settings["Export Name"] = str(widget.editLine.text())
        return settings

    def set_ui_settings(self, widget, tasks_settings):

        if len(tasks_settings) > 1:
            raise NotImplementedError

        widget.editLine.setText(tasks_settings[0]["Export Name"])

    @property
    def name(self):
        return "Vitor's Publish Plugin"

    @property
    def description(self):
        return "This plugin has a UI."

    @property
    def settings(self):
        return {
            "Export Name": {
                "type": "str",
                "default": "",
                "description": "Export name setting.",
            },
        }

    @property
    def item_filters(self):
        return ["plugin.withui"]

    def accept(self, settings, item):
        return {"accepted": True}

    def validate(self, settings, item):
        print(item, "was validated! The settings were:")
        pprint.pprint(dict(list((k, v.value) for k, v in settings.items())))
        return True

    def publish(self, settings, item):
        print(item, "was published! The settings were:")
        pprint.pprint(dict(list((k, v.value) for k, v in settings.items())))
        pass

    def finalize(self, settings, item):
        print(item, "was finalized! The settings were:")
        pprint.pprint(dict(list((k, v.value) for k, v in settings.items())))
        pass


class CustomNameWidget(QtGui.QWidget):
    def __init__(self, parent, qtwidgets, description_widget=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QVBoxLayout(self)

        # Label
        self.label = QtGui.QLabel(self)
        self.label.setText("Export Name")
        layout.addWidget(self.label)

        # Line edit
        self.editLine = QtGui.QLineEdit(self)

        # Layout
        layout.addWidget(self.editLine)

        self.setLayout(layout)

        if description_widget:
            layout.addWidget(description_widget)

        elided_label = qtwidgets.import_module("elided_label")
        long_label = elided_label.ElidedLabel(self)
        long_label.setText(
            "ASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDFASDF"
        )
        layout.addWidget(long_label)
