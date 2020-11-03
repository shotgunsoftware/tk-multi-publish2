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
from sgtk.platform.qt import QtGui

from .api import PublishManager  # noqa
from . import base_hooks  # noqa
from . import util  # noqa
from . import publish_tree_widget  # noqa


def show_dialog(app):
    """
    Show the main dialog ui

    :param app: The parent App
    """
    # defer imports so that the app works gracefully in batch modes
    from .dialog import AppDialog

    display_name = sgtk.platform.current_bundle().get_setting("display_name")

    # check for unsaved work and prompt the user if necessary
    # do not allow the user to publish, until their work has been saved to Shotgun
    show = True
    if app.require_save:
        try:
            if not app.engine.current_session_path():
                answer = QtGui.QMessageBox.question(
                    None,
                    "Save Work",
                    "Do you want to save your work to continue to publish?",
                    defaultButton=QtGui.QMessageBox.Yes,
                )

                if answer == QtGui.QMessageBox.Yes:
                    app.engine.show_save_dialog()
                    show = app.engine.current_session_path()
                else:
                    show = False

        except AttributeError as error:
            error_msg = "Error: '%s'" % error
            app.logger.error(error_msg)
            QtGui.QMessageBox.critical(
                QtGui.QApplication.activeWindow(), "File Save Error", error_msg
            )
            show = False

    if show:
        # start ui
        if app.modal:
            app.engine.show_modal(display_name, app, AppDialog)
        else:
            app.engine.show_dialog(display_name, app, AppDialog)
