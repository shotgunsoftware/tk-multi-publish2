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
import uuid
import logging
from sgtk.platform.qt import QtCore, QtGui

from .ui.details import Ui_Details

logger = sgtk.platform.get_logger(__name__)



class Details(QtGui.QWidget):
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
        self.ui = Ui_Details()
        self.ui.setupUi(self)
        self._uid = uuid.uuid4().hex

        # set up a logger
        full_log_path = "%s.%s" % (logger.name, self._uid)
        self._logger = logging.getLogger(full_log_path)

        self._handler = PublishLogHandler(self.ui.log_list)

        # and handle it in the UI
        self._logger.addHandler(self._handler)

        if sgtk.LogManager().global_debug:
            self._handler.setLevel(logging.DEBUG)
        else:
            self._handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(levelname)s %(basename)s] %(message)s"
        )
        self._handler.setFormatter(formatter)


        
    def set_description(self, description):

        self.ui.information.setText(description)

    def add_settings(self, settings):
        """
        Add a setting to the UI
        """
        for setting in settings:

            logger.info("Add setting %s" % setting)

            if setting.type == "bool":
                chk = QtGui.QCheckBox(self.ui.details_frame)
                self.ui.settings_layout.addWidget(chk)
                chk.setText(setting.name)
                chk.setToolTip(setting.description)
                if setting.default_value is not None:
                    chk.setChecked(setting.default_value)
            else:
                layout = QtGui.QHBoxLayout()
                label = QtGui.QLabel(self.ui.details_frame)
                layout.addWidget(label)
                editor = QtGui.QLineEdit(self.ui.details_frame)
                layout.addWidget(editor)
                self.ui.settings_layout.addLayout(layout)

                label.setText(setting.name)
                label.setToolTip(setting.description)
                if setting.default_value is not None:
                    editor.setText(str(setting.default_value))

        if len(settings) == 0:
            # hide settings header
            self.ui.options_header.hide()


    def get_settings(self):

        return {}

    def get_logger(self):

        return self._logger

