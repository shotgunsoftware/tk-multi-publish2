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
from .node_widget import NodeWidget

logger = sgtk.platform.get_logger(__name__)


class TreeNodeBase(QtGui.QTreeWidgetItem):
    """
    Base class for all tree widgets.

    Each of these QTreeWidgetItem objects encapsulate an
    Item widget which is used to display the actual UI
    for the tree node.
    """

    def __init__(self, parent):
        """
        :param parent: The parent QWidget for this control
        """
        super(TreeNodeBase, self).__init__(parent)

        # create an item widget and associate it with this QTreeWidgetItem
        tree_widget = self.treeWidget()
        self._node_widget = NodeWidget(tree_widget)
        tree_widget.setItemWidget(self, 0, self._node_widget)

    def begin_process(self):
        """
        Reset progress state
        """
        if self.enabled:
            # enabled nodes get a dotted ring
            self._node_widget.set_status(self._node_widget.PROCESSING)
        else:
            # unchecked items just get empty
            self._node_widget.set_status(self._node_widget.EMPTY)

    def _set_status_upwards(self, status):
        """
        Traverse all parents and set them to be a certain status
        """
        self._node_widget.set_status(status)
        if self.parent():
            self.parent()._set_status_upwards(status)

    def validate(self):
        """
        Perform validation
        """
        self._node_widget.set_status(self._node_widget.VALIDATION_COMPLETE)
        return True

    def publish(self):
        """
        Perform publish
        """
        self._node_widget.set_status(self._node_widget.PUBLISH_COMPLETE)
        return True

    def finalize(self):
        """
        Perform finalize
        """
        self._node_widget.set_status(self._node_widget.FINALIZE_COMPLETE)
        return True

    @property
    def checkbox(self):
        """
        The checkbox associated with this item
        """
        return self._node_widget.checkbox

    @property
    def icon(self):
        """
        The icon pixmap associated with this item
        """
        return self._node_widget.icon

    @property
    def enabled(self):
        """
        Returns true if the checkbox is enabled
        """
        return self._node_widget.checkbox.isChecked()


class TreeNodeContext(TreeNodeBase):
    """
    Highest level object in the tree, representing a context
    """

    def __init__(self, item, parent):
        """
        :param item:
        :param parent: The parent QWidget for this control
        """
        super(TreeNodeContext, self).__init__(parent)
        self._item = item
        self._node_widget.set_header("<b>%s</b><br>%s" % (self._item.name, self._item.display_type))
        self._node_widget.set_icon(self._item.icon)

    def __str__(self):
        return "%s %s" % (self._item.display_type, self._item.name)

    @property
    def item(self):
        """
        Associated item instance
        """
        return self._item


class TreeNodeItem(TreeNodeBase):
    """
    Tree item for a publish item
    """

    def __init__(self, item, parent):
        """
        :param item:
        :param parent: The parent QWidget for this control
        """
        super(TreeNodeItem, self).__init__(parent)
        self._item = item
        self._node_widget.set_header("<b>%s</b><br>%s" % (self._item.name, self._item.display_type))
        self._node_widget.set_icon(self._item.icon)

    def __str__(self):
        return "%s %s" % (self._item.display_type, self._item.name)

    @property
    def item(self):
        """
        Associated item instance
        """
        return self._item

class TreeNodeTask(TreeNodeBase):
    """
    Tree item for a publish task
    """

    def __init__(self, task, parent):
        """
        :param task: Task instance
        :param parent: The parent QWidget for this control
        """
        super(TreeNodeTask, self).__init__(parent)

        self._task = task

        self._node_widget.set_header(self._task.plugin.name)
        self._node_widget.set_icon(self._task.plugin.icon)
        self._node_widget.checkbox.setChecked(self._task.enabled)

        if self._task.required:
            self._node_widget.checkbox.setEnabled(False)
        else:
            self._node_widget.checkbox.setEnabled(True)


    def __str__(self):
        return self._task.plugin.name

    @property
    def task(self):
        """
        Associated task instance
        """
        return self._task

    def validate(self):
        """
        Perform validation
        """
        try:
            status = self._task.validate()
        except Exception, e:
            self._set_status_upwards(self._node_widget.VALIDATION_ERROR)
            status = False
        else:
            if status:
                self._node_widget.set_status(self._node_widget.VALIDATION_COMPLETE)
            else:
                self._set_status_upwards(self._node_widget.VALIDATION_ERROR)
        return status

    def publish(self):
        """
        Perform publish
        """
        try:
            self._task.publish()
        except Exception, e:
            self._set_status_upwards(self._node_widget.PUBLISH_ERROR)
            raise
        else:
            self._node_widget.set_status(self._node_widget.PUBLISH_COMPLETE)
        return True

    def finalize(self):
        """
        Perform finalize
        """
        try:
            self._task.finalize()
        except Exception, e:
            self._set_status_upwards(self._node_widget.FINALIZE_ERROR)
            raise
        else:
            self._node_widget.set_status(self._node_widget.FINALIZE_COMPLETE)
        return True