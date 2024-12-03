# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform.qt import QtGui
import sgtk

from .ui.more_info_widget import Ui_MoreInfoWidget

logger = sgtk.platform.get_logger(__name__)


class MoreInfoDialog(QtGui.QDialog):
    """
    A dialog to display additional logging info
    """

    def __init__(self, pixmap, message, text, parent):
        """
        :param pixmap: The pixmap to use for the message
        :param message: The one line log message
        :param text: The additional text to display
        :param parent: The parent widget
        """

        super().__init__(parent)

        # set up the UI
        self.ui = Ui_MoreInfoWidget()
        self.ui.setupUi(self)

        # set the pixmap
        if pixmap:
            self.ui.pixmap_label.setPixmap(pixmap)

        # set the label and editor text
        self.ui.message_label.setText(message)
        self.ui.text_edit.setText(str(text))

        self.setWindowTitle("Additional log info...")
        self.show()
