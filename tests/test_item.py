# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import tempfile

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import temp_env_var
from tank_test.tank_test_base import setUpModule  # noqa
from mock import patch, MagicMock

import sgtk

logger = sgtk.LogManager.get_logger(__name__)


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

                # Make sure get_property returns any value if it is set.

                # Make sure if the value is not set we get the default
                test.assertEqual(item.get_property("get_test", default_value=3), 3)

                # Then set the property to None
                item.properties.get_test = None
                # We should get it back.
                test.assertEqual(item.get_property("get_test", default_value=3), None)
                # And if we remove it we should get back to getting the default value.
                del item.properties["get_test"]
                test.assertEqual(item.get_property("get_test", default_value=3), 3)

                # Now setting a local property should take precedence over the default.
                item.local_properties.get_test = None
                test.assertEqual(item.get_property("get_test", default_value=3), None)
                # And if we remove it we should get back to getting the default value.
                del item.local_properties["get_test"]
                test.assertEqual(item.get_property("get_test", default_value=3), 3)

                # Make sure local properties take precedence over global ones.
                item.properties.get_test = 1
                item.local_properties.get_test = 2
                test.assertEqual(item.get_property("get_test", default_value=3), 2)

                # Make sure if we're trying to access the local properties in a
                # non plugin hook that the error is caught.
                del self.id
                with test.assertRaisesRegex(
                    AttributeError, "Could not determine the id for this"
                ):
                    item.local_properties["test"]

        # Make sure if we're trying to access the local properties in a non-hook
        # derived class that the error is caught
        with self.assertRaisesRegex(
            AttributeError, "Could not determine the current publish plugin when"
        ):
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
        item5 = item2.create_item("test5", "test5", "test5")

        # Ensure removing an item that is not a children raises an error.
        with self.assertRaisesRegex(sgtk.TankError, "Unable to remove child item"):
            item.remove_item(item5)

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
        """
        Ensures icon is loadable from file and cached.
        """
        # The behaviour for both is pretty much the same, so pass in the methods
        # we need to use to test the images.
        self._test_image_from_file(
            self.PublishItem.set_icon_from_path,
            self.PublishItem.icon.__get__,
            has_default_image=True,
        )

    def test_thumbnail_from_file(self):
        """
        Ensures thumbnail is loadable from file and cached.
        """
        item = self._test_image_from_file(
            self.PublishItem.set_thumbnail_from_path,
            self.PublishItem.thumbnail.__get__,
            has_default_image=False,
        )
        self.assertIsNotNone(item.get_thumbnail_as_path())

    def test_invalid_file(self):
        """
        Ensures an invalid file will be properly caught by the item.
        """
        item = self.PublishItem("test", "test", "test")
        item.set_thumbnail_from_path(__file__)
        self.assertIsNone(item.get_thumbnail_as_path())

    def test_thumbnail_from_pixmap(self):
        """
        Ensures thumbnail can be loaded from memory and can be persisted on disk.
        """

        item = self.PublishItem("test", "test", "test")

        # No thumbnail set, no nothing can be retrieved.
        self.assertIsNone(item.thumbnail)
        self.assertIsNone(item.get_thumbnail_as_path())

        # If we set the thumbnail to something that can't be saved...
        mocknail = MagicMock()
        mocknail.save = lambda unused: False
        # ... we shouldn't be getting a path to disk back.
        item.thumbnail = mocknail
        self.assertIsNone(item.get_thumbnail_as_path())

        # Set the thumbnail to valid, we should be getting a path back.
        item.thumbnail = self.image
        self.assertEqual(item.thumbnail, self.image)

        # We should also be getting a temporary path on disk for that image
        # if a path is requested
        temporary_path = item.get_thumbnail_as_path()
        self.assertIsNotNone(temporary_path)

        # As long as we don't change the thumbnail, we should be getting the
        # same path.
        self.assertEqual(item.get_thumbnail_as_path(), item.get_thumbnail_as_path())

        # Now let's change the thumbnail.
        another_icon = self.QtGui.QPixmap(self.dark_image_path)
        item.thumbnail = another_icon
        # we should still be getting a path
        self.assertIsNotNone(item.get_thumbnail_as_path())
        # But it shouldn't be the same as before.
        another_temporary_path = item.get_thumbnail_as_path()
        self.assertNotEqual(another_temporary_path, temporary_path)

        self.assertTrue(os.path.exists(temporary_path))
        self.assertTrue(os.path.exists(another_temporary_path))

        del item
        import gc

        gc.collect()

        self.assertFalse(os.path.exists(temporary_path))
        self.assertFalse(os.path.exists(another_temporary_path))

    def _test_image_from_file(self, set_path, get_image, has_default_image):
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
        default_icon = get_image(item)
        if has_default_image:
            self.assertIsNotNone(default_icon)

            # If the icon can't be loaded, we should still have one. In this case,
            # the default icon.
            set_path(item, "does_not_exist.png")
            self.assertEqual(default_icon.cacheKey(), get_image(item).cacheKey())
        else:
            self.assertIsNone(default_icon)

            # If the icon can't be loaded, we should have none.
            set_path(item, "does_not_exist.png")
            self.assertIsNone(get_image(item))

        # Now load an actual icon. We shouldn't be getting the default one anymore.
        set_path(item, self.image_path)
        if has_default_image:
            self.assertNotEqual(default_icon.cacheKey(), get_image(item).cacheKey())
        else:
            self.assertIsNotNone(get_image(item))
        # Make sure we're getting the right icon.
        self.assertEqual(get_image(item).cacheKey(), self.image.cacheKey())
        self.assertEqual(get_image(item).cacheKey(), self.image.cacheKey())

        # When the child doesn't have an icon, it should return its parent's.
        self.assertEqual(get_image(child).cacheKey(), get_image(item).cacheKey())
        return item

    def test_root(self):
        """
        Ensures a node without a parent is considered the root node.
        """
        root = self.PublishItem("some node", "some node", "some node")
        self.assertIsNone(root.parent)
        self.assertTrue(root.is_root)

    def test_persistence_flag(self):
        """
        Ensures persistence works only on nodes just under the root.
        """
        root = self.PublishItem("__root__", "__root__", "__root__")
        child = root.create_item("child", "child", "child")
        grand_child = child.create_item("grand_child", "grand_child", "grand_child")

        # Make only the items directly under the root can be persisted.
        child.persistent = True
        self.assertTrue(child.persistent)
        child.persistent = False
        self.assertFalse(child.persistent)

        # Root and grand children of the root can't be made persistent.
        self.assertFalse(grand_child.persistent)
        with self.assertRaisesRegex(sgtk.TankError, "Only top-level tree items"):
            grand_child.persistent = True
        self.assertFalse(grand_child.persistent)

        self.assertFalse(root.persistent)
        with self.assertRaisesRegex(sgtk.TankError, "Only top-level tree items"):
            root.persistent = True
        self.assertFalse(root.persistent)

        # Persistence can be turned off anytime.
        root.persistent = False
        child.persistent = False
        grand_child.persistent = False

    def test_local_properties_persistance(self):
        """
        Ensures local properties can be reloaded and reaccessed by a new
        manager instance.
        """

        # Indirectly create tasks, since we can't create them directly without a
        # PublishPluginInstance object.
        manager = self._create_manager()
        manager.collect_session()

        # Save the session to disk.
        fd, temp_file_path = tempfile.mkstemp()
        manager.save(temp_file_path)

        # Creating a second manager will force the plugins to be reloaded by it.
        new_manager = self._create_manager()

        # Loads the tree.
        new_manager.load(temp_file_path)

        with temp_env_var(TEST_LOCAL_PROPERTIES="1"):
            # Create a generator that will ensure all tasks sees the right local properties.
            def task_yielder(manager):
                nb_items_processed = 0
                for item in manager.tree:
                    for task in item.tasks:
                        (is_valid, error) = yield task
                        # The validate method of both plugins will raise an error
                        # if the the values can be retrieved.
                        # We're raising if the test passes in the validate method
                        # because we want to make sure the validate method
                        # and the validation code is actually being called. If
                        # some other error was raised due to a bug, it would be
                        # caught by the errorEqual.
                        self.assertFalse(is_valid)
                        self.assertEqual(
                            str(error), "local_properties was serialized properly."
                        )
                        nb_items_processed += 1

                # Make sure some tasks have been processed. We don't want a false-positive
                # where no items have failed publishing because somehow no tasks
                # were available due to a misconfiguration error in the test.
                self.assertNotEqual(nb_items_processed, 0)

            # Validate with our custom yielder. Each task that fails reports an error.
            self.assertEqual(len(new_manager.validate(task_yielder(new_manager))), 6)

    def _create_manager(self):
        """
        Creates a new PublishManager.
        """
        with patch("sgtk.platform.current_bundle", return_value=self.app):
            return self.PublishManager(logger)


class TestQtPixmapAvailability(PublishApiTestBase):
    def setUp(self):
        super(TestQtPixmapAvailability, self).setUp()

        # Make sure we're about to reset a flag that actually exists!
        self.assertTrue(hasattr(self.api.item, "_qt_pixmap_is_usable"))
        self._reset_pixmap_flag()

    def test_missing_qapplication(self):
        """
        Ensures a missing QApplication will not support QtPixmap usage.
        """
        with patch.object(
            sgtk.platform.qt.QtGui.QApplication, "instance", return_value=None
        ):
            self.assertFalse(self.api.item._is_qt_pixmap_usable())

        self._reset_pixmap_flag()
        self.assertTrue(self.api.item._is_qt_pixmap_usable())

    def test_missing_engine_ui(self):
        """
        Ensures an engine without UI will not support QtPixmap usage.
        """
        with patch.object(
            sgtk.platform.qt.QtGui.QApplication, "instance", return_value=None
        ):
            self.assertFalse(sgtk.platform.current_engine().has_ui)
            self.assertFalse(self.api.item._is_qt_pixmap_usable())

        self._reset_pixmap_flag()
        self.assertTrue(self.api.item._is_qt_pixmap_usable())

    def test_pixmap_methods(self):
        """
        Ensures that method that normally use pixmap to validate behave normally when it
        is not available and do validate thumbnails.
        """
        # Pretend QPixmap is not available.
        self._reset_pixmap_flag(flag_value=False)
        item = self.PublishItem("test", "test", "test")

        # passing in a invalid file should not cause any validation...
        item.set_thumbnail_from_path(__file__)
        # ... and return the file as is.
        self.assertEqual(item.get_thumbnail_as_path(), __file__)

        # We should also get a None thumbnail back.
        self.assertIsNone(item.thumbnail)

    def _reset_pixmap_flag(self, flag_value=None):
        """
        Resets the pixmap availability flag.

        :param bool flag_value: Value to set the flag. Defaults to ``None``.
        """
        self.api.item._qt_pixmap_is_usable = flag_value
