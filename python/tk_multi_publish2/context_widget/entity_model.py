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

shotgun_model = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_globals = sgtk.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
SimpleShotgunHierarchyModel = shotgun_model.SimpleShotgunHierarchyModel


class EntityModel(SimpleShotgunHierarchyModel):
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
        super(EntityModel, self).__init__(
            parent,
            bg_task_manager=bg_task_manager
        )

        self._bundle = sgtk.platform.current_bundle()
        self._current_entity = None

        # Show a hierarchy of published files. The rationale here is that
        # when you are in a DCC, your primary objective is to publish files, so
        # the hierarchy should outline items *for which files can be published.*
        published_file_entity_type = sgtk.util.get_published_file_entity_type(self._bundle.sgtk)
        self._seed = "%s.entity" % (published_file_entity_type,)


    def _load_external_data(self):
        """
        Called whenever the model is being rebuilt.

        This inserts an object representing the current entity
        """
        if self._current_entity is None:
            return

        display_name = "%s %s" % (
            shotgun_globals.get_type_display_name(self._current_entity["type"]),
            self._current_entity.get("name")
        )

        item = shotgun_model.ShotgunStandardItem(display_name)

        # associate some hierarchy-like shotgun data
        item.setData(
            {
                "ref": {"kind": "current_context", "value": self._current_entity},
            },
            SimpleShotgunHierarchyModel.SG_DATA_ROLE
        )

        # hack alert! leaky abstraction!
        # apparently need to add this in order for things to work.
        item.setData(False, self._SG_ITEM_HAS_CHILDREN)

        # add it to model
        self.appendRow(item)

    def set_entity(self, sg_entity_dict):
        """
        Clears the model and sets it up for the given entity.

        :param dict sg_entity_dict: Shotgun dict with name, id and type
        """

        root_entity = None

        if self._bundle.context.project:
            # for a project context, show items for current project
            root_entity = self._bundle.context.project

        self.load_data(
            self._seed,
            root=root_entity,
            entity_fields={"__all__": ["code"]}
        )




