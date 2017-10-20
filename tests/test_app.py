#!/usr/bin/env python
# Copyright 2017 Autodesk, Inc.  All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license agreement
# provided at the time of installation or download, or which otherwise accompanies
# this software in either electronic or hard copy form.
import sys
import os

sys.path.insert(0, "../../tk-core/python")

import sgtk


def progress_callback(value, message):
    print "[%s] %s" % (value, message)


def launch_engine():
    # Installs a StreamHandler so we see the server output in the console.
    sgtk.LogManager().initialize_base_file_handler("tk-multi-publish2.test")

    # Set the repo root environment variable that is used by the config.
    repo_root = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        ".."
    )
    repo_root = os.path.normpath(repo_root)
    os.environ["REPO_ROOT"] = repo_root

    # Authenticate
    user = sgtk.authentication.ShotgunAuthenticator().get_user()
    sg = user.create_sg_connection()

    # Bootstrap
    manager = sgtk.bootstrap.ToolkitManager(user)
    manager.plugin_id = "basic.shell"
    manager.base_configuration = "sgtk:descriptor:path?path=$REPO_ROOT/tests/fixtures/config"
    manager.do_shotgun_config_lookup = False
    manager.progress_callback = progress_callback
    return manager.bootstrap_engine(
        "tk-shell",
        sg.find_one("Project", [])
    )


def main():
    # Launch the engine.
    engine = launch_engine()
    engine.execute_command("Publish...", [])


if __name__ == "__main__":
    main()
