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
from tank_test.tank_test_base import setUpModule # noqa

from mock import MagicMock


class TestPublishItem(PublishApiTestBase):

    def test_depth_first_iteration(self):

        root = self.manager.tree.root_item
        itemA = root.create_item("item.a", "Item A", "Item A")
        itemA1 = itemA.create_item("item.a1", "Item A1", "Item A1")
        itemA2 = itemA.create_item("item.a2", "Item A2", "Item A2")

        itemB = root.create_item("item.b", "Item B", "Item B")
        itemB1 = itemB.create_item("item.b1", "Item B1", "Item B1")
        itemB2 = itemB.create_item("item.b2", "Item B2", "Item B2")

        expected_depth_first = [itemA, itemA1, itemA2, itemB, itemB1, itemB2]

        self.assertListEqual(expected_depth_first, list(self.manager.tree))

        plugin = MagicMock()
        plugin.name = "name"
        itemA.add_task(plugin)

        # make sure adding a task doesn't change the ordering, we only iterate
        # on items.
        self.assertListEqual(expected_depth_first, list(self.manager.tree))
