# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform.qt import QtCore, QtGui
import sgtk

from .ui.progress_widget import Ui_ProgressWidget
from .progress_details_widget import ProgressDetailsWidget

class ProgressWidget(QtGui.QWidget):
    """
    Progress reporting and logging
    """

    def __init__(self, parent):
        """
        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        """
        super(ProgressWidget, self).__init__(parent)

        # set up the UI
        self.ui = Ui_ProgressWidget()
        self.ui.setupUi(self)


        # parent our progress widget overlay
        self._progress_details_widget = ProgressDetailsWidget(self, self.parent())

        self.ui.details_toggle.clicked.connect(self._progress_details_widget.toggle)

    @property
    def log_tree(self):

        return self._progress_details_widget.log_tree