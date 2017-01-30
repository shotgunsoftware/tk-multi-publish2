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

HookBaseClass = sgtk.get_hook_baseclass()

class GenericSceneCollector(HookBaseClass):
    """
    Collector that operates on the maya scene
    """

    def process_current_scene(self, parent_item):
        return None

    def process_file(self, parent_item, path):

        file_name = os.path.basename(path)
        (file_name_no_ext, file_extension) = os.path.splitext(file_name)

        if file_extension in [".jpeg", ".jpg", ".png"]:
            file_item = parent_item.create_item("image_file", file_name_no_ext)
            file_item.set_thumbnail(path)
        else:
            file_item = parent_item.create_item("file", file_name_no_ext)

        file_item.properties["extension"] = file_extension
        file_item.properties["path"] = path

        return file_item


