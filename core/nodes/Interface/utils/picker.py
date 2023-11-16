import bpy


class SN_OT_Picker(bpy.types.Operator):
    bl_idname = "sn.picker"
    bl_label = "Location Picker"
    bl_description = "Pick a location in the interface"
    bl_options = {"REGISTER", "UNDO"}

    locations: bpy.props.EnumProperty(
        items=[
            ("PANEL_LOCATIONS", "Panel Locations", "Panel Locations"),
            ("PANELS", "Panels", "Panels"),
            ("MENUS", "Menus", "Menus")
        ]
    )

    def execute(self, context):
        if self.locations == "PANELS":
            register_panels()
        return {"FINISHED"}


def register_panels():
    spaces = get_space_types()
    regions = get_region_types()
    for space in spaces:
        for region in regions:
            idname = f"SN_PT_{space}_{region}"
            try:
                exec(PANEL_TEMPLATE(idname, space, region))
            except:
                pass


def get_space_types():
    return bpy.types.Panel.bl_rna.properties['bl_space_type'].enum_items.keys()


def get_region_types():
    return bpy.types.Panel.bl_rna.properties['bl_region_type'].enum_items.keys()


def PANEL_TEMPLATE(idname, space, region):
    ntree = None
    node = None
    return f"""
class {idname}(bpy.types.Panel):
    bl_label = "test"
    bl_space_type = '{space}'
    bl_region_type = '{region}'
    bl_category = 'SCRIPTING NODES'
    bl_options = {{"HIDE_HEADER"}}
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.alert = True
        row = col.row(align=True)
        row.scale_y = 2
        row.operator(
            "sn.picker", text="Select {region.replace("_", " ").title()} region in {space.replace("_", " ").title()}", icon="RESTRICT_SELECT_OFF")
        if hasattr(context.space_data, "context"):
            row = col.row(align=True)
            row.scale_y = 1.25
            row.operator("sn.picker", text=f"Select with context '{{context.space_data.context.title()}}'",
                         icon="RESTRICT_SELECT_OFF")

bpy.utils.register_class({idname})
registered_panels.append({idname})
"""
