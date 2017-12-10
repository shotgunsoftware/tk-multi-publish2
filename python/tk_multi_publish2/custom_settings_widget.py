# Copyright (c) 2017 Shotgun Software Inc
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from sgtk.platform.qt import QtGui


class CustomSettingsWidget(QtGui.QWidget):
    """
    This widget will hold the custom settings widget from a plugin.
    """

    def __init__(self, parent=None):
        """
        :param parent: QT parent object
        """
        QtGui.QWidget.__init__(self, parent)

        self._layout = QtGui.QVBoxLayout()

        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(4)
        self.setLayout(self._layout)

    @property
    def widget(self):
        """
        :returns: The custom settings ui widget, if one is specified.
        """
        if self.layout().count() == 0:
            return None
        else:
            return self.layout().itemAt(0).widget()

    @widget.setter
    def widget(self, widget):
        """
        Sets the custom settings ui widget. If there is already a custom ui,
        it is remove first.

        :param widget: Custom widget to display. If ``None``, the current UI will be cleared
            and no custom UI will be displayed.
        """
        # If there is currently a widget, clear it.
        if self.widget:
            layout = self.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # If there is an actual widget to set, set it.
        if widget:
            self.layout().addWidget(widget)
