# Copyright (c) 2026 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk.
from unittest.mock import patch

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa


class TestItemClickedHook(PublishApiTestBase):
    def test_emit_item_clicked(self):
        tree = self.manager.tree
        local_plugin = self.manager._load_publish_plugins(self.manager.context)[0]
        tree.root_item.create_item("item", "Item", "Item").add_task(local_plugin)

        tree_widget = self.PublishTreeWidget(None)
        tree_widget.set_publish_manager(self.manager)
        tree_widget.build_tree()

        from sgtk.platform.qt import QtCore

        column = 0
        tree_item = tree_widget.topLevelItem(1).child(0)
        expected_kwargs = {
            "node": tree_item,
            "widget": tree_widget.itemWidget(tree_item, column),
            "api": tree_item.get_publish_instance(),
            "buttons": QtCore.Qt.NoButton,
            "modifiers": QtCore.Qt.NoModifier,
        }
        with patch.object(tree_widget._bundle, "execute_hook_method") as mocked_execute:
            tree_widget.itemClicked.emit(tree_item, column)
            mocked_execute.assert_called_with(
                "tree_node_clicked", "single", **expected_kwargs
            )
            tree_widget.itemDoubleClicked.emit(tree_item, column)
            mocked_execute.assert_called_with(
                "tree_node_clicked", "double", **expected_kwargs
            )
