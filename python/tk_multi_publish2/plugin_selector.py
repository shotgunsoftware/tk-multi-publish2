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

from .item import Item
from .details import Details

from .ui.plugin_selector import Ui_PluginSelector

logger = sgtk.platform.get_logger(__name__)

class PluginSelector(QtGui.QWidget):
    """
    Represents an item in the left hand side list
    """

    def __init__(self, parent=None):
        """
        Constructor
        
        :param parent:          The parent QWidget for this control
        """
        QtGui.QWidget.__init__(self, parent)

        # set up the UI
        self.ui = Ui_PluginSelector()
        self.ui.setupUi(self)

        self._widgets = []


    def create_plugin(self, details_class=None):

        DetailsClass = details_class or Details

        # create widgets
        item = Item(self.ui.left_scroll_contents)
        self.ui.left_scroll_layout.addWidget(item)
        details = DetailsClass(self.ui.details_stack)
        details_index = self.ui.details_stack.addWidget(details)

        item.clicked.connect(lambda: self.select(item))

        self._widgets.append({"item": item, "details": details, "index": details_index})

        return (item, details)

    def finalize_list(self):

        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.ui.left_scroll_layout.addItem(spacerItem)


    def select(self, item):
        """
        When an item is selected
        """
        for widget in self._widgets:
            widget["item"].deselect()

        item.select()

        for widget in self._widgets:
            if widget["item"] == item:
                self.ui.details_stack.setCurrentIndex(widget["index"])

        QtGui.QApplication.processEvents()


