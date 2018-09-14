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


class TestManager(PublishApiTestBase):

    def test_file_collection(self):
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
