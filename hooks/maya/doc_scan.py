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

HookBaseClass = sgtk.get_hook_baseclass()

class MayaDocumentScanner(HookBaseClass):
    """
    Doc scan hook for maya
    """

    def scan_scene(self, log, settings):
        log.warning("yep! Settings: %s" % settings)
        return {}

