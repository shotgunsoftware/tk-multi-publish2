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

logger = sgtk.platform.get_logger(__name__)


class CustomTreeWidgetBase(QtGui.QFrame):
    """
    Widget representing a single item in the left hand side tree view.
    (Connected to a designer ui setup)

    Each item has got the following associated properties:

    - An area which can either be a checkbox for selection
      or a "dot" which signals progress updates

    - An icon

    - A header text

    These widgets are plugged in as subcomponents inside a QTreeWidgetItem
    via the PublishTreeWidget class hierarchy.
    """

    # status of checkbox / progress
    (
        NEUTRAL,
        VALIDATION,
        VALIDATION_STANDALONE,
        VALIDATION_ERROR,
        PUBLISH,
        PUBLISH_ERROR,
        FINALIZE,
        FINALIZE_ERROR,
    ) = range(8)

    def __init__(self, tree_node, parent=None):
        """
        :param parent: The parent QWidget for this control
        """
        super().__init__(parent)
        self._tree_node = tree_node

        self._icon_lookup = {
            self.NEUTRAL: None,
            self.VALIDATION: QtGui.QPixmap(":/tk_multi_publish2/status_validate.png"),
            self.VALIDATION_ERROR: QtGui.QPixmap(
                ":/tk_multi_publish2/status_warning.png"
            ),
            self.PUBLISH: QtGui.QPixmap(":/tk_multi_publish2/status_publish.png"),
            self.PUBLISH_ERROR: QtGui.QPixmap(":/tk_multi_publish2/status_error.png"),
            self.FINALIZE: QtGui.QPixmap(":/tk_multi_publish2/status_success.png"),
            self.FINALIZE_ERROR: QtGui.QPixmap(":/tk_multi_publish2/status_error.png"),
            self.VALIDATION_STANDALONE: QtGui.QPixmap(
                ":/tk_multi_publish2/status_success.png"
            ),
        }
        self._status_icon = None
        self._header = ""

    @property
    def icon(self):
        """
        The icon pixmap associated with this item
        """
        return self.ui.icon.pixmap()

    def set_icon(self, pixmap):
        """
        Set the icon to be used

        :param pixmap: Square icon pixmap to use
        """
        self.ui.icon.setPixmap(pixmap)

    @property
    def header(self):
        return self._header

    def set_header(self, title):
        """
        Set the title of the item

        :param title: Header text. Can be html.
        """
        self._header = title
        self.ui.header.setText(title)
        self.setAccessibleName(title)

    def set_checkbox_value(self, state):
        """
        Set the value of the checkbox
        """
        if state == QtCore.Qt.Checked:
            self.ui.checkbox.setCheckState(QtCore.Qt.Checked)
        elif state == QtCore.Qt.PartiallyChecked:
            self.ui.checkbox.setCheckState(QtCore.Qt.PartiallyChecked)
        else:
            self.ui.checkbox.setCheckState(QtCore.Qt.Unchecked)

    # message is for the text to be displayed on the status icon as tooltip
    def set_status(self, status, message="", info_below=True):
        """
        Set the status for the plugin
        :param status: An integer representing on of the
            status constants defined by the class
        """

        if status not in self._icon_lookup:
            raise ValueError("Invalid icon index!")

        if status == self.NEUTRAL:
            self.ui.status.hide()
        else:
            default_message = "Click for more details."
            if message:
                if info_below:
                    message += "<br>See below or click for more details."
                else:
                    message += "<br>%s" % (default_message,)
            else:
                message = default_message

            self.ui.status.setToolTip(
                QtGui.QApplication.translate(
                    "ItemWidget",
                    "<p>%s</p>" % (message,),
                    None,
                    QtGui.QApplication.UnicodeUTF8,
                )
            )

            self.ui.status.show()
            self._status_icon = QtGui.QIcon()
            self._status_icon.addPixmap(
                self._icon_lookup[status], QtGui.QIcon.Normal, QtGui.QIcon.Off
            )
            self.ui.status.setIcon(self._status_icon)
