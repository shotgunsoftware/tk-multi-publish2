# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import pprint
import traceback

import sgtk
from sgtk.util.filesystem import copy_file, ensure_folder_exists
from sgtk.platform.qt import QtGui, QtCore

HookBaseClass = sgtk.get_hook_baseclass()


class BasicFilePublishPlugin(HookBaseClass):

    def create_settings_widget(self, parent, items):
        # Create our custom widget and return it.
        # It is actually a collection of widgets parented to a single widget.
        self.review_widget = ReviewWidget(parent, self.parent.shotgun)
        return self.review_widget


    def get_ui_settings(self, widget, items):
        # This will get called when the selection changes in the UI.
        # We need to gather the settings from the UI and return them
        return {}


    def set_ui_settings(self, widget, settings, items):
        # The plugin task has just been selected in the UI, so we must set the UI state given the settings.
        # It's possible this is the first time the plugin task has been selected, in which case we won't have
        # any settings passed.
        # There also maybe multiple plugins selected in which case there might be a mix of states
        # The current implementation simply sets the settings for each settings block, so the end state of the UI
        # will represent that of the last selected item.
        widget.set_project(items[0].context)


class ReviewWidget(QtGui.QWidget):

    def __init__(self, parent, sg):
        super(ReviewWidget, self).__init__(parent)
        self.__setup_ui()

    def set_project(self, context):
        self.context_lbl.setText("Project: %s" % context.project["name"])

    def __setup_ui(self):
        """
        Creates and lays out all the Qt widgets
        :return:
        """
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(layout)
        self.context_lbl = QtGui.QLabel()
        layout.addWidget(self.context_lbl)
