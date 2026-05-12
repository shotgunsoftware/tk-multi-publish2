# Copyright (c) 2026 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import struct

import sgtk

logger = sgtk.platform.get_logger(__name__)

# TGA image type codes (header byte 2):
#   2=uncompressed RGB, 3=uncompressed grayscale
#  10=RLE RGB,          11=RLE grayscale
# Qt's TGA plugin only supports type 2.
_TGA_RLE_TYPES = (10, 11)
_TGA_UNCOMPRESSED_TYPES = (2, 3)


def is_tga_rle(path: str) -> bool:
    """Return True if the file is an RLE-encoded TGA (type 10 or 11).

    The TGA header starts with 3 bytes: [id_length, colormap_type, image_type].
    Reading only those 3 bytes is enough to determine the image type without
    parsing the full header. Types 10 (RLE RGB) and 11 (RLE grayscale) indicate
    RLE encoding, which Qt's TGA plugin cannot load.

    Returns False on any I/O error so callers can use it as a safe guard.

    :param str path: Path to the file to inspect.
    :returns: True if the file is an RLE-encoded TGA, False otherwise.
    """
    try:
        with open(path, "rb") as f:
            header = f.read(3)
        return len(header) == 3 and header[2] in _TGA_RLE_TYPES
    except OSError:
        logger.debug(f"Could not read TGA file '{path}' to check for RLE encoding.")
        return False


def tga_to_qpixmap(path: str):
    """
    Decode a TGA file (including RLE-encoded types) into a QPixmap.

    Qt's built-in TGA plugin only handles uncompressed type 2. This function
    decodes both uncompressed (type 2/3) and RLE-encoded (type 10/11) TGA files
    and constructs a QPixmap from the raw pixel data.

    Returns a null QPixmap on any decoding failure so callers can check
    ``pixmap.isNull()`` instead of catching exceptions.

    :param str path: Path to the TGA file.
    :returns: Decoded image as a QPixmap, which may be null if decoding fails.
    :rtype: QtGui.QPixmap
    """
    from sgtk.platform.qt import QtGui

    try:
        with open(path, "rb") as f:
            data = f.read()

        # Parse TGA header
        id_len = data[0]
        cmap_type = data[1]
        img_type = data[2]
        width = struct.unpack_from("<H", data, 12)[0]
        height = struct.unpack_from("<H", data, 14)[0]
        bpp = data[16]
        descriptor = data[17]
        psize = bpp // 8

        if psize not in (1, 3, 4):
            raise ValueError("unsupported bpp %d" % bpp)

        offset = 18 + id_len
        if cmap_type == 1:
            cmap_len = struct.unpack_from("<H", data, 5)[0]
            cmap_size = data[7] // 8
            offset += cmap_len * cmap_size

        # Decode pixels
        npix = width * height
        pixels = bytearray(npix * psize)
        # Use memoryview so slice assignment raises ValueError on length mismatch
        # instead of silently resizing the buffer (which would cause Qt to read
        # past the end of the data).
        mv = memoryview(pixels)

        if img_type in _TGA_RLE_TYPES:
            # RLE: alternate between run packets (repeated pixel) and raw packets
            p = offset
            o = 0
            done = 0
            while done < npix:
                head = data[p]
                p += 1
                n = (head & 0x7F) + 1
                if head & 0x80:
                    pix = data[p : p + psize]
                    p += psize
                    mv[o : o + n * psize] = pix * n
                    o += n * psize
                else:
                    size = n * psize
                    mv[o : o + size] = data[p : p + size]
                    p += size
                    o += size
                done += n
        elif img_type in _TGA_UNCOMPRESSED_TYPES:
            # Uncompressed: copy bytes directly
            mv[:] = data[offset : offset + npix * psize]
        else:
            raise ValueError("unsupported TGA image type %d" % img_type)

        if psize == 4:
            fmt = QtGui.QImage.Format_ARGB32
        elif psize == 3:
            fmt = QtGui.QImage.Format_RGB888
        else:
            fmt = QtGui.QImage.Format_Grayscale8

        img = QtGui.QImage(bytes(pixels), width, height, width * psize, fmt)
        if psize == 3:
            img = img.rgbSwapped()  # TGA stores BGR, Qt expects RGB
        if not (descriptor & 0x20):  # vertical origin: 0=bottom-left
            img = img.mirrored(False, True)
        if descriptor & 0x10:  # horizontal origin: 1=right-to-left
            img = img.mirrored(True, False)

        return QtGui.QPixmap.fromImage(img.copy())
    except Exception as e:
        logger.warning("Could not decode TGA file '%s': %s" % (path, e))
        return QtGui.QPixmap()
