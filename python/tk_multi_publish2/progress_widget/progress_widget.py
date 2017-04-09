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
from .publish_logging import PublishLogWrapper

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
        self._progress_details = ProgressDetailsWidget(self, self.parent())

        # set up our log dispatch
        self._log_wrapper = PublishLogWrapper(self._progress_details.log_tree)

        self.ui.details_toggle.clicked.connect(self._progress_details.toggle)

    @property
    def logger(self):
        return self._log_wrapper.logger

    def pop(self):
        return self._log_wrapper.pop()

    def push(self, heading, icon=None):
        return self._log_wrapper.push(heading, icon)
