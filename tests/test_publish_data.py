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


class TestPublishData(PublishApiTestBase):
    """
    Tests the PublishData class used for property bags on items and tasks.
    """

    def test_read_write_del(self):
        """
        Ensure read/write/del operations work
        """
        data = self.PublishData()

        # Test assignment
        data["test"] = 1
        self.assertEqual(data["test"], 1)
        self.assertEqual(data.test, 1)

        data.test = 2
        self.assertEqual(data["test"], 2)
        self.assertEqual(data.test, 2)

        # Test existence
        self.assertFalse(hasattr(data, "to_be_deleted"))
        data.to_be_deleted = True
        self.assertTrue(hasattr(data, "to_be_deleted"))
        self.assertTrue("to_be_deleted" in data)

        del data["to_be_deleted"]
        self.assertFalse(hasattr(data, "to_be_deleted"))
        self.assertFalse("to_be_deleted" in data)

        self.assertListEqual(list(data), ["test"])
        self.assertEqual(len(data), 1)

    def test_persistence(self):
        """
        Ensure persistence works.
        """
        data = self.PublishData()

        data.one = 1
        data.two = 2

        # We want to make sure persistence works, so we'll persist and unpersist
        # the data. Then, we'll turn the data once again back to a dict
        # so we can do a simply comparison with a dict.
        self.assertEqual(
            self.PublishData.from_dict(data.to_dict()).to_dict(), {"one": 1, "two": 2}
        )
