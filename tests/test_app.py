#!/usr/bin/env python
# Copyright 2017 Autodesk, Inc.  All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license agreement
# provided at the time of installation or download, or which otherwise accompanies
# this software in either electronic or hard copy form.
import sys

sys.path.insert(0, "../../tk-core/python")


def progress_callback(value, message):
    print("[%s] %s" % (value, message))


def launch_engine():

    # Imported locally to avoid use after bootstrap.
    import sgtk

    # Installs a StreamHandler so we see the server output in the console.
    sgtk.LogManager().initialize_base_file_handler("tk-multi-publish2.test")

    # Authenticate
    user = sgtk.authentication.ShotgunAuthenticator().get_user()
    sg = user.create_sg_connection()

    project = sg.find_one("Project", [["tank_name", "is_not", None]])
    if project is None:
        raise RuntimeError(
            "You need at least one project with the Project.tank_name field set."
        )

    # Bootstrap
    manager = sgtk.bootstrap.ToolkitManager(user)
    manager.plugin_id = "basic.shell"
    manager.base_configuration = (
        "sgtk:descriptor:path?path=$REPO_ROOT/tests/fixtures/config"
    )
    manager.do_shotgun_config_lookup = False
    manager.progress_callback = progress_callback

    return manager.bootstrap_engine("tk-shell", project)


def main():
    # Launch the engine.
    engine = launch_engine()
    engine.execute_command("Publish...", [])


if __name__ == "__main__":
    main()
