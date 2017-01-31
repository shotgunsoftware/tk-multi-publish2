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
import maya.cmds as cmds

HookBaseClass = sgtk.get_hook_baseclass()

class MayaSceneCollector(HookBaseClass):
    """
    Collector that operates on the maya scene
    """

    def process_file(self, parent_item, path):

        if path.endswith(".ma") or path.endswith(".mb"):
            file_name = os.path.basename(path)
            (file_name_no_ext, file_extension) = os.path.splitext(file_name)
            file_item = parent_item.create_item("file.maya", "Maya File", file_name)
            file_item.properties["extension"] = file_extension
            file_item.properties["path"] = path

            file_item.set_icon(os.path.join(self.disk_location, "icons", "maya.png"))

            # experimental
            file_item.properties["workspace_root"] = path

            return file_item

        else:
            return super(MayaSceneCollector, self).process_file(parent_item, path)


    def process_current_scene(self, parent_item):

        scene = self.create_current_maya_scene(parent_item)
        self.create_cameras(scene)
        self.create_playblasts(scene)
        return scene


    def create_current_maya_scene(self, parent_item):

        scene_file = cmds.file(query=True, sn=True)
        if scene_file:
            scene_file = os.path.abspath(scene_file)
            file_name = os.path.basename(scene_file)
            (file_name_no_ext, file_extension) = os.path.splitext(file_name)
            current_scene = parent_item.create_item("maya.scene", "Current Maya Scene", file_name)

        else:
            current_scene = parent_item.create_item("maya.scene", "Current Maya Scene", "Untitled")

        current_scene.properties["path"] = scene_file
        current_scene.properties["workspace_root"] = cmds.workspace( q=True, rootDirectory=True )

        current_scene.set_icon(os.path.join(self.disk_location, "icons", "maya.png"))

        return current_scene



    def create_cameras(self, parent_item):

        items = []
        for dag_path in cmds.ls(type="camera", long=True):
            short_name = dag_path.split("|")[-1]
            item = parent_item.create_item("maya.camera", "Maya Camera", short_name)
            item.properties["maya_type"] = "camera"
            item.properties["dag_path"] = dag_path
            item.set_icon(os.path.join(self.disk_location, "icons", "camera.png"))
            items.append(item)

        return items

    def create_playblasts(self, parent_item):

        # use the workspace_root property on the parent to
        # extract playblast objects
        items = []

        ws_root = parent_item.properties.get("workspace_root")
        if ws_root:
            playblast_dir = os.path.join(ws_root, "movies")
            if os.path.exists(playblast_dir):
                for filename in os.listdir(playblast_dir):
                    path = os.path.join(playblast_dir, filename)
                    item = parent_item.create_item("maya.playblast", "Playblast", filename)
                    item.properties["path"] = path
                    item.set_icon(os.path.join(self.disk_location, "icons", "popcorn.png"))
                    items.append(item)

        return items




