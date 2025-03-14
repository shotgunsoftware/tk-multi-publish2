# Copyright (c) 2017 Shotgun Software Inc
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

# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_model"
)
shotgun_view = sgtk.platform.import_framework("tk-framework-qtwidgets", "views")
shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals"
)

from .ui.settings_widget import Ui_SettingsWidget


class FieldNameLabel(QtGui.QLabel):
    """
    Wrapper class so that we can style based on class
    """

    pass


class FieldValueLabel(QtGui.QLabel):
    """
    Wrapper class so that we can style based on class
    """

    pass


class SettingsWidget(QtGui.QWidget):
    """
    Widget that shows shotgun data in a name-value pair, top down fashion:

    Status: In Progress
    Description: Foo Bar
    Created By: Sam Smith

    The widget is constructing the contents of this widget using QLabels
    which will contain clickable hyperlink fields to linked entities.
    """

    link_activated = QtCore.Signal(str)

    def __init__(self, parent):
        """
        Constructor

        :param parent: QT parent object
        """
        QtGui.QWidget.__init__(self, parent)
        self._app = sgtk.platform.current_bundle()

        # now load in the UI that was created in the UI designer
        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        # Set spacing between widgets within the settings widget
        self.layout().setSpacing(15)

        # Hide the settings scroll area until widgets are added
        self.ui.settings_scroll_area.hide()
        self._widgets = []

    def clear(self):
        """
        Clear all items in the widget
        """
        self._app.log_debug("Clearing UI...")
        # before we begin widget operations, turn off visibility
        # of the whole widget in order to avoid recomputes
        self.setVisible(False)

        try:
            for x in self._widgets:
                # remove widget from layout:
                self.ui.settings_layout.removeWidget(x)
                # set it's parent to None so that it is removed from the widget hierarchy
                x.setParent(None)
                # mark it to be deleted when event processing returns to the main loop
                x.deleteLater()

            self._widgets = []

        finally:
            # make the window visible again and trigger a redraw
            self.ui.settings_scroll_area.hide()
            self.setVisible(True)

    def set_data(self, settings):
        """
        Clear any existing data in the widget and populate it with new data

        :param settings: Shotgun data dictionary
        """

        # first clear existing stuff
        self.clear()

        if len(settings) == 0:
            # an empty dictionary indicates no data available.
            return

        self.setVisible(False)
        try:

            # now create new items - order alphabetically
            curr_row = 0

            for setting in settings:

                field_label = FieldNameLabel(self)
                field_label.setText(setting.name)
                field_label.setToolTip(setting.description)
                field_label.setWordWrap(True)
                field_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

                value_label = FieldValueLabel(self)
                value_label.setText(setting.string_value)
                value_label.setWordWrap(True)
                value_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

                self.ui.settings_layout.addWidget(field_label, curr_row, 0)
                self.ui.settings_layout.addWidget(value_label, curr_row, 1)

                self._widgets.append(value_label)
                self._widgets.append(field_label)

                curr_row += 1

            # let the value column be the expanding one
            self.ui.settings_layout.setColumnStretch(1, 1)
            # and push all rows together
            self.ui.settings_layout.setRowStretch(curr_row, 1)
        finally:
            # make the window visible again and trigger a redraw
            self.ui.settings_scroll_area.show()
            self.setVisible(True)

    def set_static_data(self, settings):
        """
        Clear any existing data in the widget and populate it with new data

        :param settings: Shotgun data dictionary
        """
        # first clear existing stuff
        self.clear()

        if len(settings) == 0:
            # an empty dictionary indicates no data available.
            return

        self.setVisible(False)
        try:

            # now create new items - order alphabetically
            curr_row = 0

            for name, value in settings:
                field_label = FieldNameLabel(self)
                field_label.setText(name)
                field_label.setWordWrap(True)
                field_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

                value_label = FieldValueLabel(self)
                value_label.setText(str(value))
                value_label.setWordWrap(True)
                value_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

                self.ui.settings_layout.addWidget(field_label, curr_row, 0)
                self.ui.settings_layout.addWidget(value_label, curr_row, 1)

                self._widgets.append(value_label)
                self._widgets.append(field_label)

                curr_row += 1

            # let the value column be the expanding one
            self.ui.settings_layout.setColumnStretch(1, 1)
            # and push all rows together
            self.ui.settings_layout.setRowStretch(curr_row, 1)
        finally:
            # make the window visible again and trigger a redraw
            self.ui.settings_scroll_area.show()
            self.setVisible(True)
