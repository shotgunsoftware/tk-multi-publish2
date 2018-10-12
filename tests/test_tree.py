# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import tempfile

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule # noqa

import sgtk


class TestPublishTree(PublishApiTestBase):

    def test_unserialized_tree_same_as_serialized(self):
        """
        Make sure that persistence doesn't lose information
        """

        # Population of the tree is made easier through the manager class, so use that

        # Indirectly create tasks, since we can't create them directly without a
        # PublishPluginInstance object.
        self.manager.collect_session()

        # Create some items that will modify
        tree = self.manager.tree
        item = tree.root_item.create_item("item.a", "Item A", "Item A")
        child = item.create_item("item.b", "Item B", "Item B")

        # Touch every property of an item.
        self._set_item(
            item, True, "Description 1", "/a/b/c.png", "/d/e/f.png", "local", "global"
        )
        self._set_item(
            child, False, "Description 2", "/g/h/i.png", "/j/k/l.png", "local2", "global2"
        )

        fd, temp_file_path = tempfile.mkstemp()
        before_load = self.manager.tree.to_dict()
        self.manager.save(temp_file_path)
        self.manager.load(temp_file_path)
        after_load = self.manager.tree.to_dict()

        self.maxDiff = None
        self.assertEqual(before_load, after_load)

    def test_bad_document_version(self):
        """
        Ensures we can't reload documents from an incorrect version.
        """
        with self.assertRaisesRegexp(sgtk.TankError, "<missing version>"):
            self.PublishTree.from_dict({})

        bad_version = 99999999
        with self.assertRaisesRegexp(sgtk.TankError, "Unrecognized serialization version \(%s\)" % bad_version):
            self.PublishTree.from_dict({"serialization_version": bad_version})

    def test_pprint(self):
        """
        Ensures pretty printing works.
        """
        self.manager.collect_session()
        self.manager.tree.pprint()

    def test_tree_clearing(self):
        """
        Ensures tree is cleared properly.
        """
        tree = self.manager.tree
        persistent = tree.root_item.create_item("persitent", "persistent", "persistent")
        persistent.persistent = True

        volatile = tree.root_item.create_item("volatile", "volatile", "volatile")
        volatile.persistent = False

        self.assertEqual(len(list(self.manager.tree)), 2)
        tree.clear(clear_persistent=False)
        self.assertEqual(len(list(self.manager.tree)), 1)
        tree.clear(clear_persistent=True)
        self.assertEqual(len(list(self.manager.tree)), 0)

    def test_clear_everything(self):
        """
        Ensures nodes are all properly deleted when calling clear.
        """
        # This test was written to ensure that all nodes are properly cleared the
        # first time we called the method. An old bug had the clear remove one item
        # out of two because we were iterating on the children of the root without
        # making a copy of the list of items to remove first. Rookie mistake. :)
        tree = self.manager.tree
        for _ in range(10):
            persistent = tree.root_item.create_item("persitent", "persistent", "persistent")
            persistent.persistent = True

        tree.clear(clear_persistent=True)
        self.assertEqual(list(self.manager.tree), [])

    def test_root_deletion(self):
        """
        Ensures you can't delete the root.
        """
        with self.assertRaisesRegexp(sgtk.TankError, "Removing the root item is not allowed."):
            self.manager.tree.remove_item(self.manager.tree.root_item)

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
                self.id = "/path/to/pluign.py"
                item.local_properties["property"] = local_prop

        # Local properties
        TestHook()
        item.properties["property"] = global_prop
