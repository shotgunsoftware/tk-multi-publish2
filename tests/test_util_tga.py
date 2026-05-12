# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import struct
import tempfile

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa

_BITS_PER_BYTE = 8
_TGA_IMG_TYPE_UNCOMPRESSED = 2
_TGA_IMG_TYPE_RLE = 10
_TGA_DESCRIPTOR_TOP_LEFT = 0x20
_TGA_RLE_RAW_PACKET_HEADER = b"\x00"
_TEST_PIXEL_VALUE = b"\x80"


def _make_tga_file(path, img_type, width=2, height=2, bpp=24):
    """
    Write a minimal valid TGA file to the given path.

    :param str path: Path to write the TGA file to.
    :param int img_type: TGA image type byte (2=uncompressed, 10=RLE).
    :param int width: Image width in pixels.
    :param int height: Image height in pixels.
    :param int bpp: Bits per pixel (24=RGB, 32=RGBA).
    """
    psize = bpp // _BITS_PER_BYTE
    # 18-byte header: descriptor=0x20 sets top-left origin (no vertical flip)
    header = struct.pack(
        "<BBBHHBHHHHBB",
        0,
        0,
        img_type,
        0,
        0,
        0,
        0,
        0,
        width,
        height,
        bpp,
        _TGA_DESCRIPTOR_TOP_LEFT,
    )
    if img_type == _TGA_IMG_TYPE_RLE:
        # RLE: each pixel as a raw packet (raw-packet header + BGR bytes)
        pixel_data = (_TGA_RLE_RAW_PACKET_HEADER + _TEST_PIXEL_VALUE * psize) * (
            width * height
        )
    else:
        pixel_data = _TEST_PIXEL_VALUE * (width * height * psize)

    with open(path, "wb") as f:
        f.write(header + pixel_data)


class TestUtilTga(PublishApiTestBase):
    """Tests for util_tga module functions."""

    def test_is_tga_rle(self):
        """
        Ensures is_tga_rle returns True for RLE type 10 and False for
        uncompressed type 2.
        """
        util_tga = self.app.import_module("tk_multi_publish2").util_tga
        with tempfile.NamedTemporaryFile(
            suffix=".tga"
        ) as rle_path, tempfile.NamedTemporaryFile(suffix=".tga") as non_rle_path:
            _make_tga_file(rle_path.name, img_type=_TGA_IMG_TYPE_RLE)
            _make_tga_file(non_rle_path.name, img_type=_TGA_IMG_TYPE_UNCOMPRESSED)
            self.assertTrue(util_tga.is_tga_rle(rle_path.name))
            self.assertFalse(util_tga.is_tga_rle(non_rle_path.name))

    def test_decode_tga_to_raw_rle(self):
        """
        Ensures decode_tga_to_raw correctly decodes an RLE TGA file:
        pixel buffer has the right length and pixel values match the encoded data.
        """
        util_tga = self.app.import_module("tk_multi_publish2").util_tga
        with tempfile.NamedTemporaryFile(suffix=".tga") as path:
            _make_tga_file(
                path.name, img_type=_TGA_IMG_TYPE_RLE, width=2, height=2, bpp=24
            )
            result = util_tga.decode_tga_to_raw(path.name)
            self.assertEqual(result["width"], 2)
            self.assertEqual(result["height"], 2)
            self.assertEqual(result["psize"], 3)
            self.assertEqual(
                len(result["pixels"]),
                result["width"] * result["height"] * result["psize"],
            )
            # Each pixel was encoded as _TEST_PIXEL_VALUE repeated for each channel (BGR)
            self.assertEqual(
                result["pixels"],
                _TEST_PIXEL_VALUE
                * result["width"]
                * result["height"]
                * result["psize"],
            )
