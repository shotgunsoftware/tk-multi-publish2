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

from mock import MagicMock

class TestPublishItem(PublishApiTestBase):

    class ItemHelper(object):

        def __init__(self, path_setter, image_getter):
            self._path_setter = path_setter
            self._image_getter = image_getter

        def image(self, item):
            return getattr(item, self._image_getter)

        def set_path(self, item, path):
            getattr(item, self._path_setter)(path)

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

    def test_task_creation(self):

        item = self.PublishItem("test", "test", "test")

        plugin = MagicMock()
        plugin.name = "first"
        item.add_task(plugin)
        item.add_task(plugin)
        item.add_task(plugin)

        self.assertEqual(len(item.tasks), 3)
        item.clear_tasks()
        self.assertEqual(len(item.tasks), 0)

    def test_property_handling(self):
        """
        Ensure's plugin data is read/written correctly to the item.
        """

        # This will allow us to differentiate between the self of the test class
        # and the self from the hook.
        test = self

        item = self.PublishItem("test", "test", "test")

        # This test is written inside a hook since local_properties expect
        # code to be running inside a hook instance.
        class PropertyTesting(sgtk.Hook):
            def __init__(self):

                # Get/set global properties
                item.properties["test"] = 1
                test.assertEqual(item.properties["test"], 1)

                # Get/set local properties, set the plugin id to 1.
                self.id = 1
                item.local_properties["test"] = 2
                test.assertEqual(item.properties["test"], 1)
                test.assertEqual(item.local_properties["test"], 2)
                test.assertEqual(item.get_property("test"), 2)

                # Change the plugin id. We should be writing to a new local
                # property set.
                self.id = 2
                item.local_properties["test"] = 3
                test.assertEqual(item.properties["test"], 1)
                test.assertEqual(item.local_properties["test"], 3)
                test.assertEqual(item.get_property("test"), 3)

                # Switch back to the previous plugin and we should now
                # have the previous values.
                self.id = 1
                test.assertEqual(item.properties["test"], 1)
                test.assertEqual(item.local_properties["test"], 2)
                test.assertEqual(item.get_property("test"), 2)

                # Make sure if we're trying to access the local properties in a
                # non plugin hook that the error is caught.
                del self.id
                with test.assertRaisesRegexp(AttributeError, "Could not determine the id for this"):
                    item.local_properties["test"]

        # Make sure if we're trying to access the local properties in a non-hook
        # derived class that the error is caught
        with self.assertRaisesRegexp(AttributeError, "Could not determine the current publish plugin when"):
            item.local_properties["test"]

        # Instantiating the class will run the rest defined above.
        PropertyTesting()

    def test_item_lifescope(self):
        """
        Ensures items can be added and removed properly.
        """
        item = self.PublishItem("test", "test", "test")

        item2 = item.create_item("test2", "test2", "test2")
        item3 = item.create_item("test3", "test3", "test3")
        item4 = item.create_item("test4", "test4", "test4")

        children = [c.name for c in item.children]
        self.assertEqual(["test2", "test3", "test4"], children)

        item.remove_item(item2)
        children = [c.name for c in item.children]
        self.assertEqual(["test3", "test4"], children)

        item.remove_item(item3)
        children = [c.name for c in item.children]
        self.assertEqual(["test4"], children)

        item.remove_item(item4)
        children = [c.name for c in item.children]
        self.assertEqual(len(list(item.children)), 0)

    def test_icon_from_file(self):
        self._test_image_from_file(
            self.ItemHelper("set_icon_from_path", "icon"),
            has_default_image=True
        )
        self._test_image_from_file(
            self.ItemHelper("set_thumbnail_from_path", "thumbnail"),
            has_default_image=False
        )

    def _test_image_from_file(self, ih, has_default_image):
        """
        Ensures images are handled properly whether they
        are loaded from disk or memory.
        """

        # In order to understand how this test works, and to make sure it
        # is easy to understand, you need to know that QPixmaps have a cache
        # key that is unique per resource. If an image is loaded from the same
        # file twice, the cache key will be the same for two different QPixmaps.
        # Oddly, two pixmaps with with the same cache key are not equal...

        item = self.PublishItem("test", "test", "test")
        child = item.create_item("child", "child", "child")

        # Make sure there is always an icon, even when none has been set.
        default_icon = ih.image(item)
        if has_default_image:
            self.assertIsNotNone(default_icon)

            # If the icon can't be loaded, we should still have one. In this case,
            # the default icon.
            ih.set_path(item, "does_not_exist.png")
            self.assertEqual(default_icon.cacheKey(), ih.image(item).cacheKey())
        else:
            self.assertIsNone(default_icon)

            # If the icon can't be loaded, we should have none.
            ih.set_path(item, "does_not_exist.png")
            self.assertIsNone(ih.image(item))

        # Now load an actual icon. We shouldn't be getting the default one anymore.
        ih.set_path(item, self.icon_path)
        if has_default_image:
            self.assertNotEqual(default_icon.cacheKey(), ih.image(item).cacheKey())
        else:
            self.assertIsNotNone(ih.image(item))
        # Make sure we're getting the right icon.
        self.assertEqual(ih.image(item).cacheKey(), self.icon.cacheKey())
        self.assertEqual(ih.image(item).cacheKey(), self.icon.cacheKey())

        # When the child doesn't have an icon, it should return its parent's.
        self.assertEqual(ih.image(child).cacheKey(), ih.image(item).cacheKey())
