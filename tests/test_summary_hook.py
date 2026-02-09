# Copyright (c) 2026 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk.

from unittest import mock

from publish_api_test_base import PublishApiTestBase
from tank_test.tank_test_base import setUpModule  # noqa


class TestSummaryHook(PublishApiTestBase):
    def check_values_match_v2_10_7(self, summary_method, expected_args):
        """Test that calling method sets expected values."""
        from sgtk.platform.qt import QtGui

        publish2 = self.app.import_module("tk_multi_publish2")
        widget = publish2.summary_overlay.SummaryOverlay(QtGui.QWidget())
        with (
            mock.patch.object(widget, "show"),
            mock.patch.object(QtGui, "QPixmap"),
            mock.patch.object(widget.ui.icon, "setPixmap"),
            mock.patch.object(widget.ui.label, "setText"),
            mock.patch.object(widget.ui.info, "setText"),
            mock.patch.object(widget.ui.publish_again, "setText"),
            mock.patch.object(widget.ui.publish_again, "setVisible"),
        ):
            patched_methods_expected_args = zip(
                [
                    QtGui.QPixmap,
                    widget.ui.label.setText,
                    widget.ui.info.setText,
                    widget.ui.publish_again.setText,
                    widget.ui.publish_again.setVisible,
                ],
                expected_args,
            )

            getattr(self.app.summary_hook, summary_method)(widget)

            assert widget.ui.icon.setPixmap.called
            for patched_method, expected_arg in patched_methods_expected_args:
                patched_method.assert_called_with(expected_arg)

    def test_no_item_error(self):
        self.check_values_match_v2_10_7(
            "no_items_error",
            [
                ":/tk_multi_publish2/publish_failed.png",
                "Could not find any\nitems to publish.",
                "For more details, <b><u>click here</u></b>.",
                "",
                False,
            ],
        )

    def test_success(self):
        self.check_values_match_v2_10_7(
            "success",
            [
                ":/tk_multi_publish2/publish_complete.png",
                "Publish\nComplete",
                "For more details, <b><u>click here</u></b>.",
                "To publish again, <b><u>click here</u></b>.",
                True,
            ],
        )

    def test_fail(self):
        self.check_values_match_v2_10_7(
            "fail",
            [
                ":/tk_multi_publish2/publish_failed.png",
                "Publish\nFailed!",
                "For more details, <b><u>click here</u></b>.",
                "",
                False,
            ],
        )

    def test_loading(self):
        self.check_values_match_v2_10_7(
            "loading",
            [
                ":/tk_multi_publish2/overlay_loading.png",
                "Loading and processing",
                "Hold tight while we analyze your data",
                "",
                False,
            ],
        )
