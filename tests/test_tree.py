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

import sgtk

from StringIO import StringIO


class TestPublishItem(PublishApiTestBase):

    maxDiff = None

    def test_persistence(self):
        """
        Make sure that persistence doesn't lose information
        """
        item = self.manager.tree.root_item.create_item("item.a", "Item A", "Item A")
        child = item.create_item("item.b", "Item B", "Item B")

        self._set_item(
            item, True, "Description 1", "/a/b/c.png", "/d/e/f.png", "local", "global"
        )
        self._set_item(
            child, False, "Description 2", "/g/h/i.png", "/j/k/l.png", "local2", "global2"
        )

        saved_tree_buff = StringIO()
        self.manager.tree.save(saved_tree_buff)
        saved_tree_str = saved_tree_buff.getvalue()

        reloaded_tree = self.manager.tree.load(StringIO(saved_tree_str))
        resaved_tree_buff = StringIO()
        reloaded_tree.save(resaved_tree_buff)

        resaved_tree_str = resaved_tree_buff.getvalue()

        self.assertEqual(saved_tree_str, resaved_tree_str)

    def _set_item(self, item, boolean, description, icon_path, thumb_path, local_prop, global_prop):
        item.active = boolean
        item.context_change_allowed = boolean
        item.enabled = boolean
        item.expanded = boolean

        item.thumbnail_enabled = boolean
        item.thumbnail_explicit = boolean

        item.description = description

        item.set_icon_from_path(icon_path)
        item.set_thumbnail_from_path(thumb_path)

        class TestHook(sgtk.Hook):
            def __init__(self):
                self.id = 1
                item.local_properties["property"] = local_prop

        # Local properties
        TestHook()
        item.properties["property"] = global_prop
