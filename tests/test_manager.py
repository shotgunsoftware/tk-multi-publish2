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

from mock import Mock, MagicMock


class TestManager(PublishApiTestBase):

    def test_file_collection(self):
        """
        Ensures files are collected only once.
        """
        A_PNG = "/a/b/c.png"
        D_PNG = "/a/b/d.png"

        # Collecting one file should result in one collected file
        collected_files = self.manager.collect_files([A_PNG])
        self.assertEqual(len(collected_files), 1)
        self.assertEqual(collected_files[0].properties.path, A_PNG)

        # Recollecting the same file should do nothing.
        self.assertEqual(len(self.manager.collect_files([A_PNG])), 0)

        # Collecting a new file should work.
        collected_files = self.manager.collect_files([D_PNG])
        self.assertEqual(len(collected_files), 1)

        # We should get all files that were collected.
        self.assertEqual(self.manager.collected_files, [A_PNG, D_PNG])

        # Turning persistence off on an item should not collect it.
        next(self.manager.tree.root_item.children).persistent = False
        self.assertEqual(self.manager.collected_files, [D_PNG])

    def test_publish_workflow(self):
        """
        Ensures the default publish workflow works.
        """
        self.manager.collect_session()
        self.manager.validate()
        self.manager.publish()
        self.manager.finalize()

    def test_validate_failures(self):
        """
        Ensures publishing and finalizing report error properly.
        """
        def test_nodes():
            one_child_item = self.PublishItem("one_child", "one_child", "one_child")

            # First yield a task that fails validation normally.
            task = MagicMock(
                item=one_child_item,
                validate=lambda: False
            )

            is_valid, error_msg = (yield task)
            self.assertFalse(is_valid)
            self.assertIsNone(error_msg)

            two_children_item = self.PublishItem("one_child", "one_child", "one_child")

            # Then yield a task that fails by raising an error
            # and has a different parent
            task = MagicMock(
                item=two_children_item,
                validate=Mock(side_effect=Exception("Test error!"))
            )

            # Invalid task should fail validation.
            is_valid, error_msg = (yield task)
            self.assertFalse(is_valid)
            self.assertEqual(error_msg, "Test error!")

            # Then yield a task that has the same parent item and
            # also fail.
            task = MagicMock(
                item=two_children_item,
                validate=lambda: False
            )
            is_valid, error_msg = (yield task)

            self.assertFalse(is_valid)
            self.assertIsNone(error_msg)

        failures = self.manager.validate(test_nodes())

        # The should be as many failures as there are failed *items*.
        # Since three tasks failed, but there were only two different
        # parent items, there should be two items.
        self.assertEqual(len(failures), 2)

    def test_publish_raise_flag(self):
        """
        Ensures an exception is raised when the raise_on_error
        flag is set.
        """
        def test_nodes():
            task = MagicMock(
                publish=Mock(side_effect=Exception("Test error!"))
            )
            error = yield task
            self.assertIsNotNone(error)
            raise error

        with self.assertRaisesRegexp(Exception, "Test error!"):
            self.manager.publish(test_nodes())

    def test_publish_and_finalize_failures(self):
        """
        Ensures publishing and finalizing report error properly.
        """
        def test_nodes():

            error = Exception("Test error!")

            task = MagicMock(
                publish=Mock(side_effect=error),
                finalize=Mock(side_effect=error)
            )
            returned_error = (yield task)

            self.assertEqual(error, returned_error)

        self.manager.publish(test_nodes())
        self.manager.finalize(test_nodes())
