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
import os
import maya.cmds as cmds

HookBaseClass = sgtk.get_hook_baseclass()

class MayaSceneCollector(HookBaseClass):
    """
    Collector that operates on the maya scene
    """

    def process_current_scene(self, create_item):

        scene = self.create_current_maya_scene(create_item)
        self.create_cameras(create_item, scene)




    def process_file(self, create_item, path):

        if path.endswith(".ma") or path.endswith(".mb"):
            file_name = os.path.basename(path)
            (file_name_no_ext, file_extension) = os.path.splitext(file_name)
            file_item = create_item("maya_file", file_name_no_ext)
            file_item.properties["extension"] = file_extension
            file_item.properties["path"] = path

        else:
            super(MayaSceneCollector, self).process_file(create_item, path)


    def create_current_maya_scene(self, create_item):

        scene_file = cmds.file(query=True, sn=True)
        if scene_file:
            scene_file = os.path.abspath(scene_file)
            file_name = os.path.basename(scene_file)
            (file_name_no_ext, file_extension) = os.path.splitext(file_name)
            current_scene = create_item("current_maya_scene", file_name_no_ext)

        else:
            current_scene = create_item("current_maya_scene", "<Untitled>")

        current_scene.properties["path"] = scene_file

        return current_scene



    def create_cameras(self, create_item, parent):

        for dag_path in cmds.ls(type="camera", long=True):
            short_name = dag_path.split("|")[-1]
            item_name = "Camera %s" % short_name
            dag_item = create_item("maya_camera", item_name, parent=parent)
            dag_item.properties["maya_type"] = "camera"
            dag_item.properties["dag_path"] = dag_path

