import bpy

from . import utils
from .describe import describe


class OBJECT_TOOLKIT_UL_sets(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_property, index
    ):
        layout.label(text=item.name, icon="GROUP")


class OBJECT_TOOLKIT_PT_object_toolkit(bpy.types.Panel):
    bl_label = "Object Toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Toolkit"

    def draw(self, context):
        if len(context.selected_objects) > 0:
            self.layout.label(
                text=f"{len(context.selected_objects)} selected",
                icon="RESTRICT_SELECT_OFF",
            )
        else:
            self.layout.label(text="Nothing selected", icon="INFO")
        col = self.layout.column(align=True)
        col.operator("object_toolkit.rename_selected", icon="SORTALPHA")
        col.operator("object_toolkit.distribute", icon="ALIGN_JUSTIFY")
        self.layout.prop(context.scene.object_toolkit, "spacing")
        self.layout.prop(context.scene.object_toolkit, "axis", expand=True)
        self.layout.operator("object_toolkit.measure", icon="DRIVER_DISTANCE")
        header, panel = self.layout.panel("OBJECT_TOOLKIT_PT_subpanel")
        header.label(text="Selection Sets")
        if panel:
            panel.template_list(
                "OBJECT_TOOLKIT_UL_sets",
                "",
                context.scene.object_toolkit,
                "sets",
                context.scene.object_toolkit,
                "active_set",
            )
            row = panel.row()
            row.operator("object_toolkit.save_selection_set", text="Save", icon="ADD")
            row.operator("object_toolkit.restore_selection_set", text="Select")
            panel.operator("object_toolkit.export_names", icon="EXPORT")
        self.layout.label(text=describe(context.active_object), icon="OBJECT_DATA")


def draw_object_menu(self, context):
    self.layout.separator(type="SPACE")
    self.layout.operator("object_toolkit.rename_selected")
    self.layout.operator("object_toolkit.distribute")


class OBJECT_TOOLKIT_MT_toolkit(bpy.types.Menu):
    bl_label = "Toolkit"

    def draw(self, context):
        pie = self.layout.menu_pie()
        column = pie.column()
        column.operator("object_toolkit.rename_selected")
        column_2 = pie.column()
        column_2.operator("object_toolkit.distribute")
        column_3 = pie.column()
        column_3.operator("object_toolkit.save_selection_set")
        column_4 = pie.column()
        column_4.operator("object_toolkit.measure")


class OBJECT_TOOLKIT_AP_preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    verbose: bpy.props.BoolProperty(
        name="Verbose", description="Print what the add-on does"
    )

    def draw(self, context):
        self.layout.prop(self, "verbose")


def register():
    bpy.types.VIEW3D_MT_object.append(draw_object_menu)
    utils.add_shortcut(
        "3D View",
        "VIEW_3D",
        "wm.call_menu_pie",
        "Q",
        properties={"name": "OBJECT_TOOLKIT_MT_toolkit"},
        shift=True,
    )


def unregister():
    bpy.types.VIEW3D_MT_object.remove(draw_object_menu)
