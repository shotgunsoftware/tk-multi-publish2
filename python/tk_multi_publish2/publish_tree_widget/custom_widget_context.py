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
from sgtk.platform.qt import QtCore
from .ui.context_widget import Ui_ContextWidget
from .custom_widget_base import CustomTreeWidgetBase


logger = sgtk.platform.get_logger(__name__)


class CustomTreeWidgetContext(CustomTreeWidgetBase):
    """
    Context display widget
    """

    def __init__(self, tree_node, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super().__init__(tree_node, parent)

        # set up the UI
        self.ui = Ui_ContextWidget()
        self.ui.setupUi(self)
        self.ui.checkbox.clicked.connect(self._on_checkbox_clicked_manually)

    @property
    def icon(self):
        """
        The icon pixmap associated with this item
        """
        return None

    def set_icon(self, pixmap):
        """
        Set the icon to be used

        :param pixmap: Square icon pixmap to use
        """
        pass

    def set_status(self, status, message="", info_below=True):
        """
        Set the status for the plugin
        :param status: An integer representing on of the
            status constants defined by the class
        """
        pass

    def _on_checkbox_clicked_manually(self):
        """
        Callback that fires when the user clicks the checkbox
        """

        # the stateChanged signal is emitted before clicked() signal, which means
        # that the value of checkState() below is the one after the user clicks the checkbox
        state = self.ui.checkbox.checkState()

        # When user clicks a context checkbox, we want it to choose between selecting all children
        # and unselecting all children, so 2 states.
        # when user clicks on the checkbox of a child of the context, we have the possibility that some children are
        # selected, and others are not. In this case we need the QtCore.Qt.PartiallyChecked state. So 3 states... but this case is
        # covered by underlying classes
        if state != QtCore.Qt.PartiallyChecked:
            self._tree_node.set_check_state(state)
        else:
            self.ui.checkbox.animateClick()
