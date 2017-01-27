# Copyright (c) 2017 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.
import sgtk
import pprint
import maya.cmds as cmds

HookBaseClass = sgtk.get_hook_baseclass()

class MayaSceneCollector(HookBaseClass):
    """
    Collector that operates on the maya scene
    """

    def collect(self, subscriptions, create_item):

        self.logger.debug("Executing collect hook")
        self.logger.debug("Subscriptions: %s" % pprint.pformat(subscriptions))


        # current scene
        scene = create_item("maya_scene", "Current Scene")

        for dag_path in cmds.ls(long=True, noIntermediate=True):
            create_item("maya_dag", dag_path, parent=scene)


        # files!
        for path in self.parent.get_external_files():
            scene = create_item("file", path)
