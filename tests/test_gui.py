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

try:
    from MA.UI import topwindows
    from MA.UI import first
    from MA.UI import holdKeys
    from MA.UI import Mouse
except ImportError:
    pytestmark = pytest.mark.skip()


# This fixture will launch tk-run-app on first usage
# and will remain valid until the test run ends.
@pytest.fixture(scope="session")
def host_application(tk_test_project, tk_test_entities):
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
            tk_test_project["type"],
            "--context-entity-id",
            str(tk_test_project["id"]),
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
        self.root = parent["Flow Production Tracking: Publish"].get()

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
        "Browse folders to publish*image sequences"
    ].exists(), "Browse folders to publish image sequences button is missing."

    # Click on Browse file to publish and then close the file explorer window
    app_dialog.root.buttons["Browse files to publish"].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].waitExist(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].buttons["Cancel"].mouseClick()

    # Click on Browse folders to publish and image sequences then close the file explorer window
    app_dialog.root.buttons["Browse folders to publish*image sequences"].mouseClick()
    app_dialog.root.dialogs["Browse folders to publish image sequences"].waitExist(
        timeout=30
    )
    app_dialog.root.dialogs["Browse folders to publish image sequences"].buttons[
        "Cancel"
    ].mouseClick()


def test_file_publish(app_dialog, tk_test_project):
    """
    Ensure you can publish an image file successfully.
    """
    # Click on Browse file to publish and then select the file to publish
    app_dialog.root.buttons["Browse files to publish"].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].waitExist(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].waitIdle(timeout=30)

    # Get image path to be published
    image_path = os.path.expandvars("${TK_TEST_FIXTURES}/files/images/svenFace.jpg")

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
    app_dialog.root["item details"].captions["svenFace.jpg"].waitExist(timeout=30)
    assert (
        app_dialog.root["context picker widget"]
        .captions["*" + tk_test_project["name"]]
        .exists()
    ), "Context is not set to Toolkit Publish2 UI Automation."

    # Change context to use a comp task from shot_001
    # Select a shot
    app_dialog.root["context picker widget"].captions[
        "*" + tk_test_project["name"]
    ].mouseClick()
    app_dialog.root["context picker widget"].textfields.typeIn("Shot_001")
    topwindows.listitems["Shot_001"].waitExist(timeout=30)
    app_dialog.root["context picker widget"].textfields.typeIn("{ENTER}")
    app_dialog.root["context picker widget"].captions["*Shot_001"].waitExist(timeout=30)
    # Select the comp task from the dropdown menu
    app_dialog.root["context picker widget"].checkboxes.mouseClick()
    app_dialog.root["context picker widget"].textfields.typeIn("{ENTER}{ENTER}")

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

    # Validate the Progress Details view
    app_dialog.root["Upper frame"].captions["For more details*"].mouseClick()
    app_dialog.root["Upper frame"].captions["Progress Details"].waitExist(timeout=30)
    # Validate Copy to clipboard button
    assert (
        app_dialog.root["Upper frame"].buttons["Copy to Clipboard"].exists()
    ), "Copy to Clipboard button is missing."
    app_dialog.root["Upper frame"].buttons["Copy to Clipboard"].mouseClick()
    # Validate the plugin is showing up.
    assert (
        app_dialog.root["Upper frame"]
        .outlineitems["File publisher plugin accepted: *svenFace.jpg"]
        .exists()
    ), "Missing File Publisher plugins"
    # Scroll down to make sure to have all second items showing up
    activityScrollBar = first(app_dialog.root.scrollbars)
    width, height = activityScrollBar.size
    # PySide2 is not able to see scrollbar position UI item
    if (
        app_dialog.root["Upper frame"].scrollbars.indicators["Position"].exists()
        is True
    ):
        app_dialog.root["Upper frame"].scrollbars.indicators["Position"].mouseSlide()
    else:
        app_dialog.root.scrollbars.mouseSlide(width * 0.5, height * -2)
    activityScrollBar.mouseDrag(width * 0.5, height * 1)
    # Validate the finalizing pass
    assert (
        app_dialog.root["Upper frame"]
        .outlineitems["DEBUG: Executing post finalize hook method..."]
        .exists()
    ), "Post finalizing hook is missing"
    assert (
        app_dialog.root["Upper frame"]
        .outlineitems["Publish Complete! For details, click here."]
        .exists()
    ), "Publish Complete! For details, click here is missing"
    # Close Progress Details view
    if app_dialog.root["Upper frame"].buttons["Close"].exists() is True:
        app_dialog.root["Upper frame"].buttons["Close"].mouseClick()
    else:
        app_dialog.root["Upper frame"].buttons[7].mouseClick()
    app_dialog.root["Upper frame"].captions["To publish again*"].waitExist(timeout=30)

    # Return to the main dialog
    app_dialog.root["Upper frame"].captions["To publish again*"].mouseClick()

    # make sure you're on the main dialog
    assert app_dialog.root.captions[
        "Drag and drop files or folders here"
    ].exists(), "Drag and drop files or folders here text is missing."
    assert app_dialog.root.buttons[
        "Browse files to publish"
    ].exists(), "Browse files to publish button is missing."
    assert app_dialog.root.buttons[
        "Browse folders to publish*image sequences"
    ].exists(), "Browse folders to publish image sequences button is missing."


def test_custom_plugin(app_dialog):
    """
    Ensure you can publish an image file successfully.
    """
    # Click on Browse file to publish and then select the file to publish
    app_dialog.root.buttons["Browse files to publish"].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].waitExist(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].waitIdle(timeout=30)

    # Get image path to be published
    image_path = os.path.expandvars("${TK_TEST_FIXTURES}/files/images/svenFace.jpg")

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

    # Validation of the Publish to Shotgun with items plugin
    # Select plugin Publish to Shotgun with items of the first item
    app_dialog.root["collected items tree"].outlineitems[
        "Publish to Flow Production Tracking with items"
    ].mouseClick()
    # Make sure the checkbox is check
    if (
        app_dialog.root["details frame"].checkboxes["Set task to in review"].checked
        is False
    ):
        app_dialog.root["details frame"].checkboxes[
            "Set task to in review"
        ].mouseClick()
    # Select plugin Publish to Shotgun with items of the second item
    app_dialog.root["collected items tree"].outlineitems[
        "Publish to Flow Production Tracking with items"
    ][1].mouseClick()
    # Make sure the checkbox is unchecked
    if (
        app_dialog.root["details frame"].checkboxes["Set task to in review"].checked
        is True
    ):
        app_dialog.root["details frame"].checkboxes[
            "Set task to in review"
        ].mouseClick()
    # Do a multiple plugins selection of item 1 and 2
    with holdKeys("{CONTROL}"):
        app_dialog.root["collected items tree"].outlineitems[
            "Publish to Flow Production Tracking with items"
        ].mouseSlide()
        Mouse.click()

    # Validate that items and set_in_review values are the right ones for each rows
    expected_results = [
        ["svenFace.jpg_sub", "*'set_in_review': False*"],
        ["svenFace.jpg", "*'set_in_review': True*"],
    ]
    # Rows and cells are not showing up with PySide2. It is only showing listitems
    if app_dialog.root["details frame"].tables.rows.exists() is True:
        row_number = 0
        for row_number, (name, state) in enumerate(expected_results):
            row_number += 1  # This is to skip the first row which is used for headers.
            assert (
                app_dialog.root["details frame"]
                .tables.rows[row_number]
                .cells[name]
                .exists()
            ), (
                "Not the right item for row "
                + str(row_number)
                + ". "
                + str(name)
                + " isn't the expected one."
            )
            assert (
                app_dialog.root["details frame"]
                .tables.rows[row_number]
                .cells[state]
                .exists()
            ), (
                "Not the right state for row "
                + str(row_number)
                + ". "
                + str(state)
                + " isn't the expected one."
            )
    else:
        for item, (name, state) in enumerate(expected_results):
            assert app_dialog.root["details frame"].listitems[name].exists(), (
                "Not the right item, " + str(name) + " isn't the expected one."
            )
            assert app_dialog.root["details frame"].listitems[state].exists(), (
                "Not the right state, " + str(state) + " isn't the expected one."
            )

    # Validation of the Publish to Shotgun without items plugin
    # Select Publish to Shotgun without items of the first item
    app_dialog.root["collected items tree"].outlineitems[
        "Publish to Flow Production Tracking without items"
    ].mouseSlide()
    Mouse.click()
    # Make sure the checkbox is check
    if (
        app_dialog.root["details frame"].checkboxes["Set task to in review"].checked
        is False
    ):
        app_dialog.root["details frame"].checkboxes[
            "Set task to in review"
        ].mouseClick()
    # Select Publish to Shotgun without items of the second item
    app_dialog.root["collected items tree"].outlineitems[
        "Publish to Flow Production Tracking without items"
    ][1].mouseClick()
    # Make sure the checkbox is unchecked
    if (
        app_dialog.root["details frame"].checkboxes["Set task to in review"].checked
        is True
    ):
        app_dialog.root["details frame"].checkboxes[
            "Set task to in review"
        ].mouseClick()
    # Go back the Publish to Shotgun without items plugin of the first item and make sure checkbox is still checked
    app_dialog.root["collected items tree"].outlineitems[
        "Publish to Flow Production Tracking without items"
    ].mouseClick()
    assert (
        app_dialog.root["details frame"].checkboxes["Set task to in review"].checked
    ), "Checkbox should be checked"

    # Click on validate button
    app_dialog.root["Bottom frame"].buttons["Validate"].mouseClick()
    assert (
        app_dialog.root["Bottom frame"]
        .captions["Validation Complete. All checks passed."]
        .exists()
    ), "Validation didn't complete successfully"

    # Return to the main dialog
    app_dialog.root["collected items tree"].outlineitems["*svenFace.jpg*"].mouseClick()
    if (
        app_dialog.root["Bottom frame"].buttons["Delete selected items"].exists()
        is True
    ):
        app_dialog.root["Bottom frame"].buttons["Delete selected items"].mouseClick()
    else:
        app_dialog.root["Bottom frame"].buttons[4].mouseClick()
    app_dialog.root.dialogs["Remove items?"].buttons["OK"].mouseClick()

    # make sure you're on the main dialog
    assert app_dialog.root.captions[
        "Drag and drop files or folders here"
    ].exists(), "Drag and drop files or folders here text is missing."
    assert app_dialog.root.buttons[
        "Browse files to publish"
    ].exists(), "Browse files to publish button is missing."
    assert app_dialog.root.buttons[
        "Browse folders to publish*image sequences"
    ].exists(), "Browse folders to publish image sequences button is missing."


def test_description_inheritance(app_dialog, tk_test_project):
    """
    Ensure summary description inheritance is working fine.
    """
    # Click on Browse file to publish and then select the file to publish
    app_dialog.root.buttons["Browse files to publish"].mouseClick()
    app_dialog.root.dialogs["Browse files to publish"].waitExist(timeout=30)
    app_dialog.root.dialogs["Browse files to publish"].waitIdle(timeout=30)

    # Get images path to be published
    # # This is commented out because it is not working on Azure!
    # image_path = os.path.normpath(
    #     os.path.expandvars(
    #         '${TK_TEST_FIXTURES}/files/images/"svenFace.jpg" "sven.png"'
    #     )
    # )
    image_path = os.path.expandvars("${TK_TEST_FIXTURES}/files/images/svenFace.jpg")

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
    app_dialog.root["item details"].captions["svenFace.jpg"].waitExist(timeout=30)

    # Open the Browse file to publish and then select the second file to publish
    app_dialog.root["button container"].navIndexes("0").mouseClick()
    # Get images path to be published
    image_path = os.path.expandvars("${TK_TEST_FIXTURES}/files/images/sven.png")
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
    app_dialog.root["item details"].captions["12 tasks to execute"].waitExist(
        timeout=30
    )
    assert (
        app_dialog.root["context picker widget"]
        .captions["*" + tk_test_project["name"]]
        .exists()
    ), "Context is not set to Toolkit Publish2 UI Automation project."

    # Add a summary description and make sure all items inherited it
    app_dialog.root.textfields.typeIn("Description Summary")
    # Make sure first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems["*svenFace.jpg*"].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Make sure first child of the first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*svenFace.jpg_sub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Make sure second child of the first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*svenFace.jpg_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Scroll down to make sure to have all second items showing up
    # PySide2 is not able to see scrollbar position UI item
    if (
        app_dialog.root["collected items tree"]
        .scrollbars.indicators["Position"]
        .exists()
        is True
    ):
        activityScrollBar = first(app_dialog.root.scrollbars)
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].scrollbars.indicators[
            "Position"
        ].mouseSlide()
        activityScrollBar.mouseDrag(width * 0, height * 1)
    else:
        activityScrollBar = first(app_dialog.root["collected items tree"])
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].mouseSlide(width * 0.97, height * 0.1)
        activityScrollBar.mouseDrag(width * 0.97, height * 1)
    # Make sure second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems["*sven.png*"].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Make sure first child of the second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems["*sven.png_sub*"].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"
    # Make sure second child of the second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*sven.png_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: Summary"]
        .exists()
    ), "Description should be inherited"

    # Add description for the first image
    # Scroll up to make sure to have all first items showing up
    # PySide2 is not able to see scrollbar position UI item
    if (
        app_dialog.root["collected items tree"]
        .scrollbars.indicators["Position"]
        .exists()
        is True
    ):
        activityScrollBar = first(app_dialog.root.scrollbars)
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].scrollbars.indicators[
            "Position"
        ].mouseSlide()
        activityScrollBar.mouseDrag(width * 0, height * 0)
    else:
        activityScrollBar = first(app_dialog.root["collected items tree"])
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].mouseSlide(width * 0.97, height * 0.8)
        activityScrollBar.mouseDrag(width * 0.97, height * 0)
    # Select the first parent item
    app_dialog.root["collected items tree"].outlineitems["*svenFace.jpg*"].mouseClick()
    # Make sure it is the right item
    assert (
        app_dialog.root["item details"].captions["svenFace.jpg"].exists()
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
        "*svenFace.jpg_sub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: svenFace.jpg"]
        .exists()
    ), "Description should be inherited"
    # Make sure second child of the first parent item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*svenFace.jpg_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: svenFace.jpg"]
        .exists()
    ), "Description should be inherited"

    # Add descriptions for the second image
    # Scroll down to make sure to have all second items showing up
    # PySide2 is not able to see scrollbar position UI item
    if (
        app_dialog.root["collected items tree"]
        .scrollbars.indicators["Position"]
        .exists()
        is True
    ):
        activityScrollBar = first(app_dialog.root.scrollbars)
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].scrollbars.indicators[
            "Position"
        ].mouseSlide()
        activityScrollBar.mouseDrag(width * 0, height * 1)
    else:
        activityScrollBar = first(app_dialog.root["collected items tree"])
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].mouseSlide(width * 0.97, height * 0.1)
        activityScrollBar.mouseDrag(width * 0.97, height * 1)
    # Select the second parent item
    app_dialog.root["collected items tree"].outlineitems["*sven.png*"].mouseClick()
    # Make sure it is the right item
    assert (
        app_dialog.root["item details"].captions["sven.png"].exists()
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
    app_dialog.root["collected items tree"].outlineitems["*sven.png_sub*"].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: sven.png"]
        .exists()
    ), "Description should be inherited"
    # Make sure second child of the second item inherited the summary description
    app_dialog.root["collected items tree"].outlineitems[
        "*sven.png_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: sven.png"]
        .exists()
    ), "Description should be inherited"

    # Add description for the first child of the first image
    # Scroll up to make sure to have all first items showing up
    # PySide2 is not able to see scrollbar position UI item
    if (
        app_dialog.root["collected items tree"]
        .scrollbars.indicators["Position"]
        .exists()
        is True
    ):
        activityScrollBar = first(app_dialog.root.scrollbars)
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].scrollbars.indicators[
            "Position"
        ].mouseSlide()
        activityScrollBar.mouseDrag(width * 0, height * 0)
    else:
        activityScrollBar = first(app_dialog.root["collected items tree"])
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].mouseSlide(width * 0.97, height * 0.8)
        activityScrollBar.mouseDrag(width * 0.97, height * 0)
    # Select the first child of the first item
    app_dialog.root["collected items tree"].outlineitems[
        "*svenFace.jpg_sub*"
    ].mouseClick()
    # Make sure it is the right item
    assert (
        app_dialog.root["item details"].captions["svenFace.jpg_sub"].exists()
    ), "Not the right tree item selected"
    # Make sure description is still inherited for item 1 first child
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: svenFace.jpg"]
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
        "*svenFace.jpg_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: svenFace.jpg_sub"]
        .exists()
    ), "Description should be inherited"

    # Add descriptions for the first child of the second image
    # Scroll down to make sure to have all second items showing up
    # PySide2 is not able to see scrollbar position UI item
    if (
        app_dialog.root["collected items tree"]
        .scrollbars.indicators["Position"]
        .exists()
        is True
    ):
        activityScrollBar = first(app_dialog.root.scrollbars)
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].scrollbars.indicators[
            "Position"
        ].mouseSlide()
        activityScrollBar.mouseDrag(width * 0, height * 1)
    else:
        activityScrollBar = first(app_dialog.root["collected items tree"])
        width, height = activityScrollBar.size
        app_dialog.root["collected items tree"].mouseSlide(width * 0.97, height * 0.1)
        activityScrollBar.mouseDrag(width * 0.97, height * 1)
    # Select the second parent item
    app_dialog.root["collected items tree"].outlineitems["*sven.png_sub*"].mouseClick()
    # Make sure it is the right item
    assert (
        app_dialog.root["item details"].captions["sven.png_sub"].exists()
    ), "Not the right tree item selected"
    # Make sure description is still inherited for item 2 first child
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: sven.png"]
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
        "*sven.png_evenmoresub*"
    ].mouseClick()
    assert (
        app_dialog.root["item details"]
        .captions["Description inherited from: sven.png_sub"]
        .exists()
    ), "Description should be inherited"
