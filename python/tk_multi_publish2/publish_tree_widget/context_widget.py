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
from .ui.context_widget import Ui_ContextWidget

logger = sgtk.platform.get_logger(__name__)


class ContextWidget(QtGui.QFrame):
    """
    Context display widget
    """

    def __init__(self, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super(ContextWidget, self).__init__(parent)

        # set up the UI
        self.ui = Ui_ContextWidget()
        self.ui.setupUi(self)


