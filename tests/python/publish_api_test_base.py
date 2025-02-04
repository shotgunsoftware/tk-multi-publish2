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
import sgtk

from tank_test.tank_test_base import TankTestBase  # noqa


class PublishApiTestBase(TankTestBase):
    """
    Baseclass for all Shotgun Utils unit tests.

    This sets up the fixtures, starts an engine and provides
    the following members:

    - self.framework_root: The path on disk to the framework bundle
    - self.engine: The test engine running
    - self.app: The test app running
    - self.framework: The shotgun utils fw running

    In your test classes, import module functionality like this::

        self.shotgun_model = self.framework.import_module("shotgun_model")

    """

    def setUp(self):
        """
        Fixtures setup
        """
        os.environ["PUBLISH2_API_TEST"] = "1"
        repo_root = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

        os.environ["REPO_ROOT"] = repo_root

        super().setUp()
        self.setup_fixtures()

        # set up an environment variable that points to the root of the
        # framework so we can specify its location in the environment fixture

        self.framework_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        os.environ["APP_ROOT"] = self.framework_root

        # Add these to mocked shotgun
        self.add_to_sg_mock_db([self.project])

        # now make a context
        context = self.tk.context_from_entity(self.project["type"], self.project["id"])

        # and start the engine
        self.engine = sgtk.platform.start_engine("tk-shell", self.tk, context)

        self.app = self.engine.apps["tk-multi-publish2"]

        self.manager = self.app.create_publish_manager()

        self.api = self.app.import_module("tk_multi_publish2").api
        self.PublishData = self.api.PublishData
        self.PublishItem = self.api.PublishItem
        self.PublishTree = self.api.PublishTree
        self.PublishManager = self.api.PublishManager
        self.PublishPluginInstance = self.api.plugins.PublishPluginInstance

        publish_tree_widget = self.app.import_module(
            "tk_multi_publish2"
        ).publish_tree_widget
        self.PublishTreeWidget = publish_tree_widget.PublishTreeWidget

        self.image_path = os.path.join(repo_root, "icon_256.png")
        self.dark_image_path = os.path.join(repo_root, "icon_256_dark.png")

        # Local import since the QtGui module is set only after engine startup.
        from sgtk.platform.qt import QtCore, QtGui

        self.QtGui = QtGui
        self.QtCore = QtCore

        # Instantiate the QApplication singleton if missing.
        if QtGui.QApplication.instance() is None:
            QtGui.QApplication([])

        self.image = QtGui.QPixmap(self.image_path)

    def tearDown(self):
        """
        Fixtures teardown
        """
        # engine is held as global, so must be destroyed.
        cur_engine = sgtk.platform.current_engine()
        if cur_engine:
            cur_engine.destroy()

        # important to call base class so it can clean up memory
        super().tearDown()
