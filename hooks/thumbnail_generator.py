# Copyright (c) 2023 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the ShotGrid Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the ShotGrid Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Autodesk.

import subprocess
import tempfile
import os

import sgtk
from tank import TankError

from sgtk.platform.qt import QtGui

HookBaseClass = sgtk.get_hook_baseclass()

logger = sgtk.platform.get_logger(__name__)


class ThumbnailGenerator(HookBaseClass):
    """Hook to generate a thumbnail automatically for a given file."""

    # -----------------------------------------------------------------------------------------
    # constants

    # Engines that support thumbnail generation. To add thumbnail generation for other engines,
    # override the _get_thumbnail_extractors_by_file_type and _get_thumbnail_extractor_data
    # hook methods to provide the necessary thumbnail extractor data for the engine.
    ALIAS = "alias"
    VRED = "vred"

    # -----------------------------------------------------------------------------------------
    # public hook methods

    def generate_thumbnail(self, input_path, context):
        """
        Generate a thumbnail from the given input file path and context.

        Return None if no thumbnail could be generated.

        :param input_path: The file path to generate a thumbnail for.
        :type input_path: str
        :param context: The current Flow Production Tracking context.
        :type context: sgtk.Context

        :return: The generated thumbnail.
        :rtype: QtGui.QPixmap
        """

        # Look up the extractor for the given file path
        _, ext = os.path.splitext(input_path)
        extractor = self._get_thumbnail_extractors_by_file_type().get(ext)
        if not extractor:
            return None

        # Get the thumbnail extractor data for the given extractor
        extractor_data = self._get_thumbnail_extractor_data().get(extractor)
        if not extractor_data:
            raise TankError(
                "Missing thumbnail extractor data for {extractor}".format(
                    extractor=extractor
                )
            )

        # Sanity check all necessary extractor data is present
        engine_name = extractor_data.get("engine")
        if not engine_name:
            raise TankError("Thumbnail extractor data missing key 'engine'")
        extractor_path = extractor_data.get("extractor_path")
        if not extractor_path:
            raise TankError("Thumbnail extractor data missing key 'extractor_path'")
        get_extractor_cmd_func = extractor_data.get("get_extractor_cmd_func")
        if not get_extractor_cmd_func:
            raise TankError("Thumbnail extractor data missing key 'get_cmds_func'")

        # Get the full path to the thumbnail extractor executable
        thumbnail_extractor_path = self._get_thumbnail_extractor_path(
            context, engine_name, extractor_path
        )
        if not thumbnail_extractor_path:
            return None

        # Create a temporary file to store the thumbnail
        output_path = tempfile.NamedTemporaryFile(
            suffix=".jpg", prefix="sgtk_thumb", delete=False
        ).name
        try:
            # Get the thumbnail extractor command that will generate the thumbnail
            extractor_cmd = get_extractor_cmd_func(
                thumbnail_extractor_path, input_path, output_path
            )
            # Execute the thumbnail extraction command
            success = self._execute_command(extractor_cmd)
            if not success:
                error_msg = "Failed to generate thumbnail for {input_path}".format(
                    input_path=input_path
                )
                logger.error(error_msg)
                raise TankError(error_msg)

            # Return the thumbnail as a pixmap
            return QtGui.QPixmap(output_path)
        finally:
            # Clean up the temporary file used to store the thumbnail.
            try:
                os.remove(output_path)
            except Exception:
                pass

    # -----------------------------------------------------------------------------------------
    # protected hook methods

    def _get_thumbnail_extractors_by_file_type(self):
        """
        Return a mapping of file extensions to thumbnail extractors.

        Override this hook method to support more file types.

        :return: A mapping of file extensions to thumbnail extractors.
        :rtype: dict
        """

        return {
            ".wire": self.ALIAS,
            ".vpb": self.VRED,
        }

    def _get_thumbnail_extractor_data(self):
        """
        Return a mapping of thumbnail extractors to their respective extractor data.

        The extractor data is used to automatically generate a thumbnail from a file.
        The extractor data must include:

            engine:
                type: str
                description: Name of the Toolkit engine that will be used to generate the
                    thumbnail. The engine will be used to locate the engine's software
                    executable path, which is then used to locate the thumbnail extractor
                    executable file.

            extractor_path:
                type: str
                description: The relative file path from the engine's software executable
                    path to the thumbnail extractor executable.

            get_extractor_cmd_func:
                type: str
                description: A function that takes position parameters (1) path to the
                    thumbnail extractor executable, (2) path to the input file, and (3)
                    path to the output file, and returns a list of commands that can be
                    passed to a subprocess to execute.

        Override this hook method to support more thumbnail extractors.

        :return: A mapping of thumbnail extractors to theri respective extractor data.
        :rtype: dict
        """

        return {
            self.ALIAS: {
                "engine": "tk-alias",
                "extractor_path": "thumbnail.exe",
                "get_extractor_cmd_func": self._get_alias_extractor_cmd,
            },
            self.VRED: {
                "engine": "tk-vred",
                "extractor_path": "extractMetaData.exe",
                "get_extractor_cmd_func": self._get_vred_extractor_cmd,
            },
        }

    def _get_thumbnail_extractor_path(self, context, engine_name, extractor_path):
        """
        Get the thumbnail extractor executable path for the engine.

        The thumbnail extractor executable path is determined by finding the engine's software
        executable path.

        :param context: The Toolkit context used to create an engine launcher that can
            determine the engine software location.
        :type context: sgtk.Context
        :param engine_name: The name of the engine.
        :type engine_name: str
        :param extractor_path: The relative file path from the engine's software location, to
            the thumbnail extractor executable.
        :type extractor_path: str

        :return: The thumbnail extractor executable path relative to the engine's software
            location.
        :rtype: str
        """

        # Create the engine laucnher in order to discover the engine's software location
        launcher = sgtk.platform.create_engine_launcher(
            self.parent.sgtk, context, engine_name
        )
        software_versions = launcher.scan_software()
        if not software_versions:
            return None

        # Iterate through the software versions starting from the latest version, and return
        # the first thumbnail extractor executable path found
        for software_version in reversed(software_versions):
            software_exe_path = software_version.path
            bin_path = os.path.dirname(software_exe_path)
            thumbnail_extractor_path = os.path.join(bin_path, extractor_path)
            if os.path.exists(thumbnail_extractor_path):
                return thumbnail_extractor_path

        # No thumbnail extractor executable path found
        return None

    def _execute_command(self, cmd):
        """
        Run a subprocess to execute the given command.

        :param cmd: The command to execute.
        :type cmd: list

        :return: True if the command executed successfully; otherwise, False.
        :rtype: bool
        """

        logger.info("Running thumbnail command: {}".format(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p_output, p_error = p.communicate()
        if p.returncode != 0 or p_error:
            logger.error("{}. Error {}".format(p_output, p_error))
            return False
        return True

    # -----------------------------------------------------------------------------------------
    # Engine specific extractor functions

    def _get_alias_extractor_cmd(
        self, thumbnail_extractor_path, input_path, output_path
    ):
        """
        Return a command to execute to extract a thumbnail from an Alias file.

        The command is a list of arguments that can be passed to a subprocess to execute.

        This function is used by the Alias extractor to determine the command to execute
        in order to generate a thumbnail from an Alias file.

        :param thumbnail_extractor_path: The path to the thumbnail extractor executable.
        :type thumbnail_extractor_path: str
        :param input_path: The path to the input file.
        :type input_path: str
        :param output_path: The path to the output file.
        :type output_path: str

        :return: A command to execute to extract a thumbnail from an Alias file.
        :rtype: List
        """

        return [
            thumbnail_extractor_path,
            "x",
            input_path,
            output_path,
        ]

    def _get_vred_extractor_cmd(
        self, thumbnail_extractor_path, input_path, output_path
    ):
        """
        Return a command to execute to extract a thumbnail from an VRED file.

        The command is a list of arguments that can be passed to a subprocess to execute.

        This function is used by the VRED extractor to determine the command to execute
        in order to generate a thumbnail from a VRED file.

        :param thumbnail_extractor_path: The path to the thumbnail extractor executable.
        :type thumbnail_extractor_path: str
        :param input_path: The path to the input file.
        :type input_path: str
        :param output_path: The path to the output file.
        :type output_path: str

        :return: A command to execute to extract a thumbnail from an VRED file.
        :rtype: List
        """

        return [
            thumbnail_extractor_path,
            "--icv",
            output_path,
            input_path,
        ]
