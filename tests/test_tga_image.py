# Copyright (c) 2026 Shotgun Software Inc.
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

_FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__), "fixtures", "files", "images"
)
_RLE_TGA_PATH = os.path.join(_FIXTURES_DIR, "test_rle.tga")
_UNCOMPRESSED_TGA_PATH = os.path.join(_FIXTURES_DIR, "test_uncompressed.tga")


class TestTgaImage(PublishApiTestBase):
    """Tests for tga_image module functions."""

    def test_is_tga_rle(self):
        """
        Ensures is_tga_rle returns True for RLE type 10 and False for
        uncompressed type 2.
        """
        tga_image = self.app.import_module("tk_multi_publish2").utils.tga_image
        self.assertTrue(tga_image.is_tga_rle(_RLE_TGA_PATH))
        self.assertFalse(tga_image.is_tga_rle(_UNCOMPRESSED_TGA_PATH))

    def test_tga_to_qpixmap_rle(self):
        """
        Ensures tga_to_qpixmap correctly decodes an RLE TGA file:
        the returned QPixmap is non-null and has the correct dimensions.
        """
        tga_image = self.app.import_module("tk_multi_publish2").utils.tga_image
        pixmap = tga_image.tga_to_qpixmap(_RLE_TGA_PATH)
        self.assertIsNotNone(pixmap)
        self.assertFalse(pixmap.isNull())
        self.assertEqual(pixmap.width(), 2)
        self.assertEqual(pixmap.height(), 2)
