# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa


class TestPublishTreeWidget(PublishApiTestBase):
    def test_parent_partially_checked(self):
        """
        If we have a bunch of active tasks followed by a bunch of inactive tasks, the addition
        of the inactive tasks does not trigger an update of the parent's checkbox (because the update
        relies on the checkbox.state_changed and the default is unchecked, so inactive tasks do not
        trigger a state change). Test that we are forcing a recalculation to keep the parent's check_state
        correct in all situations
        """
        tree = self.manager.tree
        item = tree.root_item.create_item("item.parent", "Parent", "Parent")
        publish_plugins = self.manager._load_publish_plugins(item.context)

        item.add_task(publish_plugins[0])
        item.add_task(publish_plugins[0])

        item.tasks[0]._active = True
        item.tasks[1]._active = False

        tree_widget = self.PublishTreeWidget(None)
        tree_widget.set_publish_manager(self.manager)
        tree_widget.build_tree()

        project_item = tree_widget.topLevelItem(1)
        parent_item = project_item.child(0)
        self.assertEqual(parent_item.check_state, self.QtCore.Qt.PartiallyChecked)

    def test_parent_checked_children_unchecked(self):
        """
        If a parent item is active and only has inactive tasks, make sure that when the
        tree is built the parent item's check_state is valid and is set to unchecked
        """
        tree = self.manager.tree
        item = tree.root_item.create_item("item.parent", "Parent", "Parent")
        publish_plugins = self.manager._load_publish_plugins(item.context)

        item.add_task(publish_plugins[0])
        item.add_task(publish_plugins[0])

        item._active = True
        item.tasks[0]._active = False
        item.tasks[1]._active = False

        tree_widget = self.PublishTreeWidget(None)
        tree_widget.set_publish_manager(self.manager)
        tree_widget.build_tree()

        project_item = tree_widget.topLevelItem(1)
        parent_item = project_item.child(0)
        self.assertEqual(parent_item.check_state, self.QtCore.Qt.Unchecked)

    def test_next_check_state(self):
        """
        Make sure the tristate checkbox on an item goes from Partially checked to
        Checked to Unchecked every time it is clicked
        """

        tree = self.manager.tree
        item = tree.root_item.create_item("item.parent", "Parent", "Parent")
        publish_plugins = self.manager._load_publish_plugins(item.context)

        item.add_task(publish_plugins[0])
        item.add_task(publish_plugins[0])

        item._active = True
        item.tasks[0]._active = False
        item.tasks[1]._active = True

        tree_widget = self.PublishTreeWidget(None)
        tree_widget.set_publish_manager(self.manager)
        tree_widget.build_tree()

        project_item = tree_widget.topLevelItem(1)
        parent_item = project_item.child(0)

        from sgtk.platform.qt import QtCore

        # Make sure the states go PartiallyChecked -> Checked -> Unchecked
        self.assertEqual(parent_item.check_state, QtCore.Qt.PartiallyChecked)
        parent_item._embedded_widget.ui.checkbox.nextCheckState()
        self.assertEqual(parent_item.check_state, QtCore.Qt.Checked)
        parent_item._embedded_widget.ui.checkbox.nextCheckState()
        self.assertEqual(parent_item.check_state, QtCore.Qt.Unchecked)
