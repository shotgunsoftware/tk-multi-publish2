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

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa

from unittest.mock import Mock, MagicMock


class TestManager(PublishApiTestBase):
    def test_file_collection(self):
        """
        Ensures files are collected only once.
        """
        A_PNG = os.path.normpath("/a/b/c.png")
        D_PNG = os.path.normpath("/a/b/d.png")

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
        one_child_item = self.PublishItem("one_child", "one_child", "one_child")
        two_children_item = self.PublishItem("two_child", "two_child", "two_child")
        error_to_raise = Exception("Test error!")

        task_1 = MagicMock(item=one_child_item, validate=lambda: False)

        task_2 = MagicMock(
            item=two_children_item, validate=Mock(side_effect=error_to_raise)
        )

        task_3 = MagicMock(item=two_children_item, validate=lambda: False)

        def test_nodes():
            # First yield a task that fails validation normally.
            is_valid, error_msg = yield task_1
            self.assertFalse(is_valid)
            self.assertIsNone(error_msg)

            # Then yield a task that fails by raising an error
            # and has a different parent
            # Invalid task should fail validation.
            is_valid, error = yield task_2
            self.assertFalse(is_valid)
            self.assertEqual(error, error_to_raise)

            # Then yield a task that has the same parent item and
            # also fail.
            is_valid, error_msg = yield task_3

            self.assertFalse(is_valid)
            self.assertIsNone(error_msg)

        failures = self.manager.validate(test_nodes())

        # The should be as many failures as there are failed *items*.
        # Since three tasks failed, but there were only two different
        # parent items, there should be two items.
        self.assertEqual(
            failures, [(task_1, None), (task_2, error_to_raise), (task_3, None)]
        )

    def test_publish_raise_flag(self):
        """
        Ensures an exception is raised when the raise_on_error
        flag is set.
        """

        def test_nodes():
            task = MagicMock(publish=Mock(side_effect=Exception("Test error!")))
            error = yield task
            self.assertIsNotNone(error)
            raise error

        with self.assertRaisesRegex(Exception, "Test error!"):
            self.manager.publish(test_nodes())

    def test_finalize_failures(self):
        """
        Ensures finalizing report exceptions properly and do not abort the finalize process.
        """
        error = Exception("Test error!")

        task = MagicMock(finalize=Mock(side_effect=error))

        def test_nodes():
            returned_error = yield task

            self.assertEqual(error, returned_error)

        with self.assertRaisesRegex(Exception, "Test error!"):
            self.manager.finalize(test_nodes())

    def test_publish_failures(self):
        """
        Ensures finalizing report exceptions properly and do not abort the finalize process.
        """

        def test_nodes():
            task = MagicMock(publish=Mock(side_effect=Exception("Test error!")))
            yield task

        with self.assertRaisesRegex(Exception, "Test error!"):
            self.manager.publish(test_nodes())
