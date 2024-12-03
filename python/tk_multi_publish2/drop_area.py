# Copyright (c) 2017 Shotgun Software Inc
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from tank.platform.qt import QtCore, QtGui


def drop_area(cls):
    """
    A class decorator which adds needed overrides to any QWidget
    so it can behave like a drop area and emit something_dropped signals

    @todo - move this into the qtwidgets framework
    """

    class WrappedClass(cls):
        """
        Wrapping class
        """

        # Emitted when something is dropped on the widget
        something_dropped = QtCore.Signal(list)

        def __init__(self, *args, **kwargs):
            """
            Instantiate the class and enable drops

            :param args: Arbitrary list of parameters used in base class init
            :param args: Arbitrary dictionary of parameters used in base class init
            """
            super().__init__(*args, **kwargs)
            self.setAcceptDrops(True)
            self._set_property("dragging", False)
            self._restrict_to_ext = []

        # Override dragEnterEvent
        def dragEnterEvent(self, event):
            """
            Check if we can handle the drop, basically if we will receive local file path

            :param event: A QEvent
            """
            # Set a property which can used to change the look of the widget
            # in a style sheet using a pseudo state, e.g. :
            # DropAreaLabel[dragging="true"] {
            #     border: 2px solid white;
            # }
            if event.mimeData().hasFormat("text/plain"):
                event.accept()
            elif event.mimeData().hasFormat("text/uri-list"):
                for url in event.mimeData().urls():
                    # We don't activate the dragging state unless ext is valid.
                    self._set_property("dragging", True)
                    # Accept if there is at least one local file
                    if _is_local_file(url):
                        event.accept()
                        break
                else:
                    event.ignore()
            else:
                event.ignore()

        # Override dragLeaveEvent
        def dragLeaveEvent(self, event):
            """
            Just unset our dragging property

            :param event: A QEvent
            """
            self._set_property("dragging", False)

        # Override dropEvent
        def dropEvent(self, event):
            """
            Process a drop event, build a list of local files and emit somethingDropped if not empty

            :param event: A QEvent
            """
            self._set_property("dragging", False)
            urls = event.mimeData().urls()
            contents = None
            if urls:
                if sgtk.util.is_macos():
                    # Fix for Yosemite and later, file paths are not actual file paths
                    # but weird /.file/id=6571367.18855673 values
                    # https://bugreports.qt-project.org/browse/QTBUG-24379
                    # https://gist.github.com/wedesoft/3216298
                    try:
                        # Custom Python (e.g. brewed ones) might not be able to
                        # import Foundation. In that case we do nothing and keep
                        # urls as they are, assuming the problem should be fixed
                        # in custom Python / PyQt / PySide
                        import Foundation

                        fixed_urls = []
                        for url in urls:
                            # It is fine to pass a regular file url to this method
                            # e.g. file:///foo/bar/blah.ext
                            fu = Foundation.NSURL.URLWithString_(
                                url.toString()
                            ).filePathURL()
                            fixed_urls.append(QtCore.QUrl(str(fu)))
                        urls = fixed_urls
                    except:
                        pass
                contents = [x.toLocalFile() for x in urls if _is_local_file(x)]
            elif event.mimeData().hasFormat("text/plain"):
                contents = [event.mimeData().text()]
            if contents:
                event.accept()
                self.something_dropped.emit(contents)
            else:
                event.ignore()

        def _set_property(self, name, value):
            """
            Helper to set custom properties which can be used in style sheets
            Set the value and do a unpolish / polish to force an update

            :param name: A property name
            :param value: A value for this property
            """
            self.setProperty(name, value)
            # We are using a custom property in style sheets
            # we need to force a style sheet re-computation with
            # unpolish / polish
            self.style().unpolish(self)
            self.style().polish(self)

    return WrappedClass


@drop_area
class DropAreaFrame(QtGui.QFrame):
    pass


def _is_local_file(url):
    """
    Helper to determine if a url is of a local file scheme

    :param url: Url object to verify whether it is a local file or not
    :returns: True if the url is a local file. False otherwise
    """
    return (hasattr(url, "isLocalFile") and url.isLocalFile()) or url.scheme() == "file"
