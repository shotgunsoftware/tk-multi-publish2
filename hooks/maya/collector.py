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
import os
import time
import maya.cmds as cmds

HookBaseClass = sgtk.get_hook_baseclass()

class MayaSceneCollector(HookBaseClass):
    """
    Collector that operates on the maya scene
    """

    def collect(self, subscriptions, item_handler):



        # item: {type: maya_dag, options: {type: camera}}


        if cmds.ls(geometry=True, long=True, noIntermediate=True):
            items.append({"type":"geometry", "name":"All Scene Geometry"})

        item  = item_handler.create_item(parent=item)

