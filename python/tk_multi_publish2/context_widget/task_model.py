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

# import the shotgun_model and view modules from the shotgun utils framework
shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
ShotgunModel = shotgun_model.ShotgunModel


class TaskModel(ShotgunModel):
    """
    Hierarchy navigation model to drive the entity combo
    dropdown :class:`EntityComboBox`.
    """

    def __init__(self, parent, bg_task_manager):
        """
        Initializes a Shotgun Hierarchy model instance.

        :param parent: The model parent.
        :type parent: :class:`~PySide.QtGui.QObject`
        :param bg_task_manager: Background task manager to use for any asynchronous work.
        :type bg_task_manager: :class:`~task_manager.BackgroundTaskManager`
        """
        super(TaskModel, self).__init__(
            parent,
            download_thumbs=False,
            bg_task_manager=bg_task_manager
        )
        self._bundle = sgtk.platform.current_bundle()
        self._current_entity = None


    def _load_external_data(self):
        """
        Called whenever the model is being rebuilt.

        This inserts an object representing the current entity
        """
        if self._current_entity is None:
            # create a "please select a task" item
            display_name = "Please select a task"
        else:
            display_name = "%s %s" % (
                shotgun_globals.get_type_display_name(self._current_entity["type"]),
                self._current_entity.get("name")
            )

        item = shotgun_model.ShotgunStandardItem(display_name)

        # associate some hierarchy-like shotgun data
        item.setData(
            self._current_entity,
            ShotgunModel.SG_DATA_ROLE
        )

        # hack alert! leaky abstraction!
        # apparently need to add this in order for things to work.
        item.setData(False, self._SG_ITEM_HAS_CHILDREN)

        # add it to model
        self.appendRow(item)

    def set_task(self, sg_entity, sg_task):
        """
        Clears the model and sets it up for the given entity.

        :param dict sg_entity: Associated entity. Shotgun dict with name, id and type
        :param dict sg_task: Shotgun dict with name, id and type
        """
        self._current_entity = sg_task

        self._load_data(
            entity_type="Task",
            filters=[["entity", "is", sg_entity]],
            hierarchy=["content"],
            fields=["content"]
        )

        self._refresh_data()



