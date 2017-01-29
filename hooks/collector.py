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

class GenericSceneCollector(HookBaseClass):
    """
    Collector that operates on the maya scene
    """

    def collect(self, subscriptions, create_item):

        print "collect generic"

        self.logger.debug("Executing collect hook")
        self.logger.debug("Subscriptions: %s" % pprint.pformat(subscriptions))

        # # Shotgun DEBUG (0.002s): collector: Subscriptions: [
        # {'type': 'current_maya_scene'},
        # {'maya_type': 'camera', 'type': 'maya_node'},
        # {'maya_type': 'camera', 'type': 'maya_node'}]  #

        # this collector handles maya stuff and files

        types = [x["type"] for x in subscriptions]

        if "file" in types:
            # we have plugins which need files
            for path in self.parent.get_external_files():

                file_name = os.path.basename(path)
                (file_name_no_ext, file_extension) = os.path.splitext(file_name)
                file_item = create_item("file", file_name_no_ext)
                file_item.properties["extension"] = file_extension
                file_item.properties["path"] = path
                if file_extension == ".png":
                    file_item.set_thumbnail(path)

