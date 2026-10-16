# SPDX-License-Identifier: GPL-3.0-or-later

import bpy

from . import _sn_helpers, interface, logic, operators, properties

classes = (
    properties.OBJECT_TOOLKIT_PG_selection_set,
    properties.OBJECT_TOOLKIT_PG_scene_properties,
    interface.OBJECT_TOOLKIT_UL_sets,
    interface.OBJECT_TOOLKIT_PT_object_toolkit,
    interface.OBJECT_TOOLKIT_MT_toolkit,
    interface.OBJECT_TOOLKIT_AP_preferences,
    operators.OBJECT_TOOLKIT_OT_rename_selected,
    operators.OBJECT_TOOLKIT_OT_distribute,
    operators.OBJECT_TOOLKIT_OT_save_selection_set,
    operators.OBJECT_TOOLKIT_OT_restore_selection_set,
    operators.OBJECT_TOOLKIT_OT_export_names,
    operators.OBJECT_TOOLKIT_OT_measure,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    properties.register()
    interface.register()
    logic.register()


def unregister():
    logic.unregister()
    interface.unregister()
    properties.unregister()
    _sn_helpers.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
