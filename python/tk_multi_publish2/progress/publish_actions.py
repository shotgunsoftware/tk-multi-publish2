# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys
import sgtk
from sgtk.platform.qt import QtCore, QtGui

logger = sgtk.platform.get_logger(__name__)

from .more_info_dialog import MoreInfoDialog


def show_folder(path):
    """
    Show the supplied path in the filesystem.

    :param path: The path to show.
    """

    # make sure we have a folder
    launch_path = os.path.dirname(path) if not os.path.isdir(path) else path

    if sgtk.util.is_linux():
        cmd = 'xdg-open "%s"' % launch_path
    elif sgtk.util.is_macos():
        cmd = 'open "%s"' % launch_path
    elif sgtk.util.is_windows():
        cmd = 'cmd.exe /C start "Folder" "%s"' % launch_path
    else:
        logger.error("Don't know how to launch browser for '%s'." % (sys.platform,))
        return

    exit_code = os.system(cmd)
    if exit_code != 0:
        logger.error("Failed to launch '%s'!" % cmd)


def show_in_shotgun(entity):
    """
    Show the supplied path in Shotgun

    :param entity: A standard PTR entity dictionary containing at least the
        "type" and "id" fields.
    """

    publisher = sgtk.platform.current_bundle()

    url = "%s/detail/%s/%d" % (publisher.sgtk.shotgun_url, entity["type"], entity["id"])

    try:
        logger.debug("Opening entity url: '%s'." % (url,))
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
    except Exception as e:
        logger.error("Failed to open url: '%s'. Reason: %s" % (url, e))


def show_more_info(pixmap, message, text, parent):
    """
    Shows additional information in a popup dialog.

    :param text: The formatted text to display.
    """

    try:
        MoreInfoDialog(pixmap, message, text, parent)
    except Exception as e:
        logger.error("Failed to launch more info dialog. Reason: %s" % (e,))


def open_url(url):
    """
    Opens the supplied url via desktop services.

    :param url: The url to open
    """

    try:
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
    except Exception as e:
        logger.error("Failed to launch more info dialog. Reason: %s" % (e,))
