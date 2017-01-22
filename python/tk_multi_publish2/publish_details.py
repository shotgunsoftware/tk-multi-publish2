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

from .ui.publish_details import Ui_PublishDetails

logger = sgtk.platform.get_logger(__name__)

class PublishDetails(QtGui.QWidget):
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
        self.ui = Ui_PublishDetails()
        self.ui.setupUi(self)
        
