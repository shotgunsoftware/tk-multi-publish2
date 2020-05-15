# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import pytest
import subprocess
import time
import os
import sys
import sgtk

try:
    from MA.UI import topwindows
    from MA.UI import first
except ImportError:
    pytestmark = pytest.mark.skip()


@pytest.fixture(scope="session")
def context():
    # A task in Big Buck Bunny which we're going to use
    # for the current context.
    return {"type": "Project", "id": 70}


# This fixture will launch tk-run-app on first usage
# and will remain valid until the test run ends.
@pytest.fixture(scope="session")
def host_application(context):
    """
    Launch the host application for the Toolkit application.

    TODO: This can probably be refactored, as it is not
    likely to change between apps, except for the context.
    One way to pass in a context would be to have the repo being
    tested to define a fixture named context and this fixture
    would consume it.
    """
    process = subprocess.Popen(
        [
            "python",
            "-m",
            "tk_toolchain.cmd_line_tools.tk_run_app",
            # Allows the test for this application to be invoked from
            # another repository, namely the tk-framework-widget repo,
            # by specifying that the repo detection should start
            # at the specified location.
            "--location",
            os.path.dirname(__file__),
            "--context-entity-type",
            context["type"],
            "--context-entity-id",
            str(context["id"]),
        ]
    )
    try:
        yield
    finally:
        # We're done. Grab all the output from the process
        # and print it so that is there was an error
        # we'll know about it.
        stdout, stderr = process.communicate()
        sys.stdout.write(stdout or "")
        sys.stderr.write(stderr or "")
        process.poll()
        # If returncode is not set, then the process
        # was hung and we need to kill it
        if process.returncode is None:
            process.kill()
        else:
            assert process.returncode == 0


@pytest.fixture(scope="session")
def app_dialog(host_application):
    """
    Retrieve the application dialog and return the AppDialogAppWrapper.
    """
    before = time.time()
    while before + 30 > time.time():
        if sgtk.util.is_windows():
            app_dialog = AppDialogAppWrapper(topwindows)
        else:
            app_dialog = AppDialogAppWrapper(topwindows["python"])

        if app_dialog.exists():
            yield app_dialog
            app_dialog.close()
            return
    else:
        raise RuntimeError("Timeout waiting for the app dialog to launch.")


class AppDialogAppWrapper(object):
    """
    Wrapper around the app dialog.
    """

    def __init__(self, parent):
        """
        :param root:
        """
        self.root = parent["Shotgun: Publish"].get()

    def exists(self):
        """
        ``True`` if the widget was found, ``False`` otherwise.
        """
        return self.root.exists()

    def close(self):
        self.root.buttons["Close"].mouseClick()


def test_app(app_dialog):
    # Make sure items are showing up
    assert app_dialog.root.captions[
        "Drag and drop files or folders here"
    ].exists(), "Drag and drop files or folders here text is missing."
    assert app_dialog.root.buttons[
        "Browse files to publish"
    ].exists(), "Browse files to publish button is missing."
    assert app_dialog.root.buttons[
        "Browse sequences to publish"
    ].exists(), "Browse folders to publish image sequences button is missing."


def test_click(app_dialog):
    # Click on Browse file to publish and then close the file explorer window
    app_dialog.root.buttons["Browse files to publish"].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].waitExist(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].buttons["Cancel"].mouseClick()

    # Click on Browse folders to publish and image sequences then close the file explorer window
    app_dialog.root.buttons["Browse sequences to publish"].mouseClick()
    app_dialog.root.dialogs["Browse folders to publish image sequences"].waitExist(
        timeout=30
    )
    app_dialog.root.dialogs["Browse folders to publish image sequences"].buttons[
        "Cancel"
    ].mouseClick()


def test_file_publish(app_dialog):
    # Click on Browse file to publish and then select the file to publish
    app_dialog.root.buttons["Browse files to publish"].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].waitExist(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].waitIdle(timeout=30)

    # Get image path to be published
    image_path = os.path.expandvars(
        "${SHOTGUN_CURRENT_REPO_ROOT}/tests/fixtures/files/images/achmed.JPG"
    )

    # Type in image path
    app_dialog.root.dialogs["Browse files to publish"].textfields[
        "File name:"
    ].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].textfields["File name:"].pasteIn(
        image_path
    )
    app_dialog.root.dialogs["Browse files to publish"].textfields[
        "File name:"
    ].waitIdle(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].textfields["File name:"].typeIn(
        "{ENTER}"
    )

    # Validate file to publish is there and the right project is selected
    app_dialog.root.captions["achmed.JPG"].waitExist(timeout=30)
    assert app_dialog.root.captions[
        "*Demo: Animation"
    ].exists(), "Context is not set to Demo: Animation project."

    # Click on validate button
    app_dialog.root.buttons["Validate"].mouseClick()
    assert app_dialog.root.captions[
        "Validation Complete. All checks passed."
    ].exists(), "Validation didn't complete successfully"

    # Publish
    app_dialog.root.buttons["Publish"].mouseClick()
    app_dialog.root.captions["Publish Complete! For details, click here."].waitExist(
        timeout=30
    )
    assert app_dialog.root.captions[
        "Publish Complete! For details, click here."
    ].exists(), "Publish failed."
