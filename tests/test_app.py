#!/usr/bin/env python
# Copyright 2017 Autodesk, Inc.  All rights reserved.
#
# Use of this software is subject to the terms of the Autodesk license agreement
# provided at the time of installation or download, or which otherwise accompanies
# this software in either electronic or hard copy form.
import os
import sys
import tempfile

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

    # when running the tests, if "api" agument comes after the script, only run
    # the API tests, non-ui
    if sys.argv[-1].lower() == "api":
        os.environ["PUBLISH2_API_TEST"] = "1"

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

def api_tests(engine):

    # api-only tests!
    publish_app = engine.apps["tk-multi-publish2"]
    manager = publish_app.create_publish_manager()
    manager.collect_session()

    # print the collected tree to the shell
    print "\n-------------"
    print "PUBLISH TREE:"
    print "-------------"
    manager.tree.pprint()

    # NOTE: the following is meant to roughly simulate how you could process
    # a publish tree, and defer some plugins to a separate execution. In this
    # case, there are some plugins with a setting that indicates they shouldn't
    # be run on the artist's machine. We process the validation locally (e.g.
    # the user is making sure the settings are set they way they'd like). The
    # publish/validate is then executed by supplying task generators that only
    # deal with the local tasks (by inspecting the plugin settings).
    #
    # NOTE: This is running without a UI, so we can supply custom task
    # generators via the api. When combining UI validation with remote
    # publish/finalize, you'll need to defer the execution in the plugin itself
    # (since the UI will always operate on all active/checked items/tasks. The
    # generic_remote plugin used here has an example of how this could be done
    # by simply checking if the publisher is running with a UI and skipping
    # execution if the run_on_farm setting is set to True.
    #
    # After validation below, the publish tree is then serialized to disk and
    # loaded by a separate manager instance. The new manager executes the
    # publish/finalize using a task generator that only yields plugins with the
    # remote execution setting set to True. This is a simple pattern to
    # test/demonstrate how this could be done.
    #
    # NOTE: The below does not accurately test remote publishing of a serialized
    # tree. That requires a completely separate process with a separate
    # `sys.modules` to load from (due to Tk's unique import namespacing).
    # Context matching is also something that is trivialized here. In a real
    # test, there'd need to be assurance that the publish is executing in the
    # same context. That's ignored/assumed here since the test app is only using
    # the first project context returned from SG.

    # simulate processing tasks locally
    print "\nSimulate validate/publish/finalize on local machine..."
    print "\n--------------------------------------------------"
    print "Local Validation: all should validate successfully."
    print "---------------------------------------------------"
    manager.validate(task_generator=all_tasks_generator(manager.tree))
    print "\n----------------------------------------------------"
    print "Local Publish: Only local plugins should be executed."
    print "-----------------------------------------------------"
    manager.publish(task_generator=local_tasks_generator(manager.tree))

    print "\n-----------------------------------------------------"
    print "Local Finalize: Only local plugins should be executed."
    print "-----------------------------------------------------"
    manager.finalize(task_generator=local_tasks_generator(manager.tree))

    # save publish tree to disk
    pub_file_dir = tempfile.mkdtemp()
    pub_file_path = os.path.join(pub_file_dir, "publish_tree.pub")
    manager.tree.save_file(pub_file_path)
    print "\nSaved publish tree to disk: %s" % (pub_file_path,)

    # now imagine the rest of this code executing on another machine

    print "\nLoading publish tree from disk..."
    manager2 = publish_app.create_publish_manager()
    manager2.load(pub_file_path)

    # simulate processing tasks remotely (would be executed on farm machine)
    print "\nSimulate publish/finalize on remote machine..."
    print "\n------------------------------------------------------"
    print "Remote Publish: Only remote plugins should be executed."
    print "-------------------------------------------------------"
    manager2.publish(task_generator=farm_tasks_generator(manager2.tree))
    print "\n-------------------------------------------------------"
    print "Remote Finalize: Only remote plugins should be executed."
    print "-------------------------------------------------------"
    manager2.finalize(task_generator=farm_tasks_generator(manager2.tree))


def all_tasks_generator(tree):
    for item in tree:
        print "%s" % (item,)
        for task in item.tasks:
            print "  %s: EXECUTING" % (task,)
            result = yield task


def local_tasks_generator(tree):

    for item in tree:
        print "%s" % (item,)
        for task in item.tasks:
            # if the plugin doesn't have a setting to "run on farm" that is True...
            if not task.plugin.settings.get("run_on_farm"):
                print "  %s: EXECUTING" % (task,)
                result = yield task
            else:
                print "  %s: NOT EXECUTING" % (task,)

def farm_tasks_generator(tree):

    for item in tree:
        print "%s" % (item,)
        for task in item.tasks:
            # if the plugin has a setting to "run on farm" that is True...
            if task.plugin.settings.get("run_on_farm"):
                print "  %s: EXECUTING" % (task,)
                result = yield task
            else:
                print "  %s: NOT EXECUTING" % (task,)


def main():
    # Launch the engine.
    engine = launch_engine()

    if "PUBLISH2_API_TEST" in os.environ:
        api_tests(engine)
    else:
        engine.execute_command("Publish...", [])


if __name__ == "__main__":
    main()
