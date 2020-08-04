# Copyright (c) 2020 Shotgun Software Inc.
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
from tank_vendor import shotgun_api3

try:
    from MA.UI import topwindows
    from MA.UI import first
except ImportError:
    pytestmark = pytest.mark.skip()


@pytest.fixture(scope="session")
def context():
    # A task in Toolkit UI Automation project which we're going to use
    # for the current context.
    # Get crendentials from TK_TOOLCHAIN env vars
    sg = shotgun_api3.Shotgun(
        os.environ["TK_TOOLCHAIN_HOST"],
        login=os.environ["TK_TOOLCHAIN_USER_LOGIN"],
        password=os.environ["TK_TOOLCHAIN_USER_PASSWORD"],
    )
    # Make sure there is not already an automation project created
    filters = [["name", "is", "Toolkit UI Automation"]]
    existed_project = sg.find_one("Project", filters)
    if existed_project is not None:
        sg.delete(existed_project["type"], existed_project["id"])
    # Get the animation template project id to be passed in the project creation
    filters = [["name", "is", "Animation Template"]]
    template_project = sg.find_one("Project", filters)
    # Create a new project with the Animation Template
    data = {
        "sg_description": "Project Created by Automation",
        "name": "Toolkit UI Automation",
        "layout_project": {"type": template_project["type"], "id": template_project["id"]},
    }
    new_project = sg.create("Project", data)
    return new_project


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
            "--config",
            "tests/fixtures/configInheritance",
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


def test_browse_buttons(app_dialog):
    """
    Ensure app dialog items are availible and that browse to publish buttons are opening file browser dialogs.
    """
    # Make sure items are available
    assert app_dialog.root.captions[
        "Drag and drop files or folders here"
    ].exists(), "Drag and drop files or folders here text is missing."
    assert app_dialog.root.buttons[
        "Browse files to publish"
    ].exists(), "Browse files to publish button is missing."
    assert app_dialog.root.buttons[
        "Browse sequences to publish"
    ].exists(), "Browse folders to publish image sequences button is missing."

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
    """
    Ensure you can publish an image file successfully.
    """
    # Click on Browse file to publish and then select the file to publish
    app_dialog.root.buttons["Browse files to publish"].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].waitExist(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].waitIdle(timeout=30)

    # Get image path to be published
    image_path = os.path.expandvars("${TK_TEST_FIXTURES}/files/images/achmed.JPG")

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
    app_dialog.root["item details"].captions["achmed.JPG"].waitExist(timeout=30)
    assert (
        app_dialog.root["context picker widget"]
        .captions["*Toolkit UI Automation"]
        .exists()
    ), "Context is not set to Toolkit UI Automation."

    # Click on validate button
    app_dialog.root["Bottom frame"].buttons["Validate"].mouseClick()
    assert (
        app_dialog.root["Bottom frame"]
        .captions["Validation Complete. All checks passed."]
        .exists()
    ), "Validation didn't complete successfully"

    # Publish
    app_dialog.root["Bottom frame"].buttons["Publish"].mouseClick()
    app_dialog.root.captions["Publish Complete! For details, click here."].waitExist(
        timeout=30
    )
    assert (
        app_dialog.root["Bottom frame"]
        .captions["Publish Complete! For details, click here."]
        .exists()
    ), "Publish failed."
    assert (
        app_dialog.root["Upper frame"].captions["Publish*Complete"].exists()
    ), "Publish failed."

    # Return to the main dialog
    app_dialog.root["Upper frame"].captions["To publish again, click here"].mouseClick()

    # make sure you're on the main dialog
    assert app_dialog.root.captions[
        "Drag and drop files or folders here"
    ].exists(), "Drag and drop files or folders here text is missing."
    assert app_dialog.root.buttons[
        "Browse files to publish"
    ].exists(), "Browse files to publish button is missing."
    assert app_dialog.root.buttons[
        "Browse sequences to publish"
    ].exists(), "Browse folders to publish image sequences button is missing."


def test_description_inheritance(app_dialog):
    """
    Ensure summary description inheritance is working fine.
    """
    # Click on Browse file to publish and then select the file to publish
    app_dialog.root.buttons["Browse files to publish"].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].waitExist(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].waitIdle(timeout=30)

    # Get images path to be published
    image_path = os.path.expandvars(
        '${TK_TEST_FIXTURES}/files/images/"achmed.JPG" "attarder.jpg"'
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
    app_dialog.root["item details"].captions["Publish Summary"].waitExist(timeout=30)
    app_dialog.root["item details"].captions["6 tasks to execute"].waitExist(timeout=30)
    assert (
        app_dialog.root["context picker widget"]
        .captions["*Toolkit UI Automation"]
        .exists()
    ), "Context is not set to Toolkit UI Automation project."

    # Add a summary description and make sure all items inherited it
    app_dialog.root.textfields.typeIn("Description Summary")
    # Make sure first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems["*achmed.JPG*"].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Make sure first child of the first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*achmed.JPG_sub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Make sure second child of the first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*achmed.JPG_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Scroll down to make sure to have all second items showing up
    activityScrollBar = first(app_dialog.root.scrollbars)
    width, height = activityScrollBar.size
    app_dialog.root.scrollbars.mouseSlide()
    activityScrollBar.mouseDrag(width * 0, height * 1)
    # Make sure second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems["*attarder.jpg*"].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Make sure first child of the second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*attarder.jpg_sub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Make sure second child of the second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*attarder.jpg_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"

    # Add description for the first image
    # Scroll up to make sure to have all first items showing up
    activityScrollBar = first(app_dialog.root.scrollbars)
    width, height = activityScrollBar.size
    app_dialog.root.scrollbars.mouseSlide()
    activityScrollBar.mouseDrag(width * 0, height * 0)
    # Select the first parent item
    app_dialog.root["collected items tree"].outlineitems["*achmed.JPG*"].mouseClick()
    # Make sure it is the right item
    assert (
        app_dialog.root["item details"].captions["achmed.JPG"].exists()
    ), "Not the right tree item selected"
    app_dialog.root["item details"].textfields["item description"].typeIn(
        "Description for item 1"
    )
    # Make sure description is not inherited
    assert (
        app_dialog.root["item details"].captions["Description not inherited"].exists()
    ), "Description should not be inherited"
    # Make sure first child of the first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*achmed.JPG_sub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: achmed.JPG"]
        .exists()
    ), "Description should be inherited"
    # Make sure second child of the first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*achmed.JPG_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: achmed.JPG"]
        .exists()
    ), "Description should be inherited"

    # Add descriptions for the second image
    # Scroll down to make sure to have all second items showing up
    activityScrollBar = first(app_dialog.root.scrollbars)
    width, height = activityScrollBar.size
    app_dialog.root.scrollbars.mouseSlide()
    activityScrollBar.mouseDrag(width * 0, height * 1)
    # Select the second parent item
    app_dialog.root["collected items tree"].outlineitems["*attarder.jpg*"].mouseClick()
    # Make sure it is the right item
    assert (
        app_dialog.root["item details"].captions["attarder.jpg"].exists()
    ), "Not the right tree item selected"
    # Make sure description is still inherited for item 2
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    app_dialog.root["item details"].textfields["item description"].typeIn(
        "Description for item 2"
    )
    # Make sure description is no more inherited
    assert (
        app_dialog.root["item details"].captions["Description not inherited"].exists()
    ), "Description should not be inherited"
    # Make sure first child of the second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*attarder.jpg_sub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: attarder.jpg"]
        .exists()
    ), "Description should be inherited"
    # Make sure second child of the second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*attarder.jpg_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: attarder.jpg"]
        .exists()
    ), "Description should be inherited"

    # Add description for the first child of the first image
    # Scroll up to make sure to have all first items showing up
    activityScrollBar = first(app_dialog.root.scrollbars)
    width, height = activityScrollBar.size
    app_dialog.root.scrollbars.mouseSlide()
    activityScrollBar.mouseDrag(width * 0, height * 0)
    # Select the first child of the first item
    app_dialog.root["collected items tree"].outlineitems[
        "*achmed.JPG_sub*"
    ].mouseClick()
    # Make sure it is the right item
    assert (
        app_dialog.root["item details"].captions["achmed.JPG_sub"].exists()
    ), "Not the right tree item selected"
    # Make sure description is still inherited for item 1 first child
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: achmed.JPG"]
        .exists()
    ), "Description should be inherited"
    app_dialog.root["item details"].textfields["item description"].typeIn(
        "Description of the first child for item 1"
    )
    # Make sure description is not inherited
    assert (
        app_dialog.root["item details"].captions["Description not inherited"].exists()
    ), "Description should not be inherited"
    # Make sure second child of the first parent item inherited the first child description
    app_dialog.root["collected items tree"].outlineitems[
        "*achmed.JPG_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: achmed.JPG_sub"]
        .exists()
    ), "Description should be inherited"

    # Add descriptions for the first child of the second image
    # Scroll down to make sure to have all second items showing up
    activityScrollBar = first(app_dialog.root.scrollbars)
    width, height = activityScrollBar.size
    app_dialog.root.scrollbars.mouseSlide()
    activityScrollBar.mouseDrag(width * 0, height * 1)
    # Select the second parent item
    app_dialog.root["collected items tree"].outlineitems[
        "*attarder.jpg_sub*"
    ].mouseClick()
    # Make sure it is the right item
    assert (
        app_dialog.root["item details"].captions["attarder.jpg_sub"].exists()
    ), "Not the right tree item selected"
    # Make sure description is still inherited for item 2 first child
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: attarder.jpg"]
        .exists()
    ), "Description should be inherited"
    app_dialog.root["item details"].textfields["item description"].typeIn(
        "Description of the first child for item 2"
    )
    # Make sure description is no more inherited
    assert (
        app_dialog.root["item details"].captions["Description not inherited"].exists()
    ), "Description should not be inherited"
    # Make sure second child of the second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*attarder.jpg_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: attarder.jpg_sub"]
        .exists()
    ), "Description should be inherited"
