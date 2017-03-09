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
import re
import time
import glob
import maya.cmds as cmds

HookBaseClass = sgtk.get_hook_baseclass()


class MayaScenePublishPlugin(HookBaseClass):
    """
    Plugin for versioning and publishing the current maya scene
    """

    @property
    def icon(self):
        """
        Path to an png icon on disk
        """
        return os.path.join(self.disk_location, "icons", "shotgun.png")

    @property
    def name(self):
        """
        One line display name describing the plugin
        """
        return "Publish Maya Scene"

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This
        can contain simple html for formatting.
        """
        return """Publishes the current maya scene. This will create a versioned backup and publish that."""

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to recieve
        through the settings parameter in the accept, validate, publish and
        finalize methods.

        A dictionary on the following form::

            {
                "Settings Name": {
                    "type": "settings_type",
                    "default": "default_value",
                    "description": "One line description of the setting"
            }

        The type string should be one of the data types that toolkit accepts
        as part of its environment configuration.
        """
        return {
            "Publish Type": {
                "type": "shotgun_publish_type",
                "default": "Maya Scene",
                "description": "Shotgun publish type to associate publishes with."
            },
        }

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.
        Only items matching entries in this list will be presented
        to the accept() method. Strings can contain glob patters
        such as *, for example ["maya.*", "file.maya"]
        """
        return ["maya.scene"]

    def accept(self, log, settings, item):
        """
        Method called by the publisher to determine if an item
        is of any interest to this plugin. Only items matching
        the filters defined via the item_filters property will
        be presented to this method.

        A publish task will be generated for each item accepted
        here. Returns a dictionary with the following booleans:

            - accepted: Indicates if the plugin is interested in
                        this value at all.
            - required: If set to True, the publish task is
                        required and cannot be disabled.
            - enabled:  If True, the publish task will be
                        enabled in the UI by default.

        :param log: Logger to output feedback to.
        :param settings: Dictionary of Settings. The keys are strings, matching the keys
            returned in the settings property. The values are `Setting` instances.
        :param item: Item to process
        :returns: dictionary with boolean keys accepted, required and enabled
        """
        project_root = item.properties["project_root"]
        context_file = os.path.join(project_root, "shotgun.context")
        log.debug("Looking for context file in %s" % context_file)
        if os.path.exists(context_file):
            try:
                with open(context_file, "rb") as fh:
                    context_str = fh.read()
                context_obj = sgtk.Context.deserialize(context_str)
                item.context = context_obj
            except Exception, e:
                log.warning("Could not read saved context %s: %s" % (context_file, e))

        return {"accepted": True, "required": False, "enabled": True}

    def validate(self, log, settings, item):
        """
        Validates the given item to check that it is ok to publish.
        Returns a boolean to indicate validity. Use the logger to
        output further details around why validation has failed.

        :param log: Logger to output feedback to.
        :param settings: Dictionary of Settings. The keys are strings, matching the keys
            returned in the settings property. The values are `Setting` instances.
        :param item: Item to process
        :returns: True if item is valid, False otherwise.
        """
        if item.properties["path"] is None:
            log.error("Please save your scene before you continue!")
            return False

        if item.properties["project_root"] is None:
            log.warning("Your scene is not part of a maya project.")

        # indicate that we are publishing this
        item.properties["is_published"] = True

        return True

    def _maya_find_additional_scene_dependencies(self):
        """
        Find additional dependencies from the scene
        """
        # default implementation looks for references and
        # textures (file nodes) and returns any paths that
        # match a template defined in the configuration
        ref_paths = set()

        # first let's look at maya references
        ref_nodes = cmds.ls(references=True)
        for ref_node in ref_nodes:
            # get the path:
            ref_path = cmds.referenceQuery(ref_node, filename=True)
            # make it platform dependent
            # (maya uses C:/style/paths)
            ref_path = ref_path.replace("/", os.path.sep)
            if ref_path:
                ref_paths.add(ref_path)

        # now look at file texture nodes
        for file_node in cmds.ls(l=True, type="file"):
            # ensure this is actually part of this scene and not referenced
            if cmds.referenceQuery(file_node, isNodeReferenced=True):
                # this is embedded in another reference, so don't include it in the
                # breakdown
                continue

            # get path and make it platform dependent
            # (maya uses C:/style/paths)
            texture_path = cmds.getAttr("%s.fileTextureName" % file_node).replace("/", os.path.sep)
            if texture_path:
                ref_paths.add(texture_path)

        return ref_paths

    def publish(self, log, settings, item):
        """
        Executes the publish logic for the given
        item and settings. Use the logger to give
        the user status updates.

        :param log: Logger to output feedback to.
        :param settings: Dictionary of Settings. The keys are strings, matching the keys
            returned in the settings property. The values are `Setting` instances.
        :param item: Item to process
        """
        # save the maya scene
        log.info("Saving maya scene...")
        cmds.file(save=True, force=True)

        scene_folder = os.path.dirname(item.properties["path"])
        filename = os.path.basename(item.properties["path"])
        publish_folder = os.path.join(scene_folder, "publishes")
        sgtk.util.filesystem.ensure_folder_exists(publish_folder)

        # figure out if we got any publishes already
        # determine highest version

        (filename_no_ext, extension) = os.path.splitext(filename)
        # strip the period off the extension
        extension = extension[1:]

        glob_pattern = os.path.join(publish_folder, "%s.v[0-9][0-9][0-9].%s" % (filename_no_ext, extension))
        log.debug("Looking for %s" % glob_pattern)

        published_files = glob.glob(glob_pattern)

        log.debug("Got %s" % published_files)

        higest_version_found = 0
        for published_file in published_files:
            # check if path matches pattern fooo.v123.ext
            version = re.search(".*\.v([0-9]+)\.%s$" % extension, published_file)
            if version:
                version_no_leading_zeroes = version.group(1).lstrip("0")
                if int(version_no_leading_zeroes) > higest_version_found:
                    higest_version_found = int(version_no_leading_zeroes)

        version_to_use = higest_version_found + 1

        publish_path = os.path.join(publish_folder, "%s.v%03d.%s" % (filename_no_ext, version_to_use, extension))

        log.info("Will publish to %s" % publish_path)

        sgtk.util.filesystem.copy_file(item.properties["path"], publish_path)

        # Create the TankPublishedFile entity in Shotgun
        args = {
            "tk": self.parent.sgtk,
            "context": item.context,
            "comment": item.description,
            "path": publish_path,
            "name": filename,
            "version_number": version_to_use,
            "thumbnail_path": item.get_thumbnail_as_path(),
            "published_file_type": settings["Publish Type"].value,
            #"dependency_paths": self._maya_find_additional_scene_dependencies(), # need to update core for this to work
        }

        sg_data = sgtk.util.register_publish(**args)

        item.properties["shotgun_data"] = sg_data
        item.properties["shotgun_publish_id"] = sg_data["id"]
        item.properties["publish_path"] = publish_path
        item.properties["publish_version"] = version_to_use


    def finalize(self, log, settings, item):
        """
        Execute the finalization pass. This pass executes once
        all the publish tasks have completed, and can for example
        be used to version up files.

        :param log: Logger to output feedback to.
        :param settings: Dictionary of Settings. The keys are strings, matching the keys
            returned in the settings property. The values are `Setting` instances.
        :param item: Item to process
        """
        project_root = item.properties["project_root"]
        context_file = os.path.join(project_root, "shotgun.context")
        with open(context_file, "wb") as fh:
            fh.write(item.context.serialize(with_user_credentials=False))




