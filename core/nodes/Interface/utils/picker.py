import bpy

class SN_OT_Picker(bpy.types.Operator):
    bl_idname = "sn.picker"
    bl_label = "Location Picker"
    bl_description = "Pick a location in the interface"
    bl_options = {"REGISTER", "UNDO"}

    options: bpy.props.EnumProperty(
        items=[
            ("PANEL_LOCATIONS", "Panel Locations", "Panel Locations"),
            ("PANELS", "Panels", "Panels"),
            ("MENUS", "Menus", "Menus")
        ]
    )

    def execute(self, context):
        if self.options == "PANELS":
            register_panels()


def register_panels():
    spaces = get_space_types()
    regions = get_region_types()

def get_space_types():
    spaces = []
    for cls in bpy.types.Space.__subclasses__():
        spaces.append(cls.bl_rna.identifier)
    return spaces

def get_region_types():
    return bpy.types.Region.bl_rna.properties["type"].enum_items.keys()


PANEL_TEMPLATE = f"""
class {idname}(bpy.types.Panel):
    bl_label = "test"
    bl_space_type = '{space}'
    bl_region_type = '{region}'
    bl_category = 'SERPENS'
    bl_options = {{"HIDE_HEADER"}}
    bl_order = 0
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.5
        row.alert = True
        op = row.operator("sn.pick_panel_location", text="Select {space.replace("_", " ").title()} {region.replace("_", " ").title()}")
        op.node_tree = "{ntree}"
        op.node = "{node}"
        op.space = "{space}"
        op.region = "{region}"
        op.context = ""
        if hasattr(context.space_data, "context"):
            row = layout.row()
            row.scale_y = 1.5
            row.alert = True
            op = row.operator("sn.pick_panel_location", text="Select {space.replace("_", " ").title()} {region.replace("_", " ").title()} "+context.space_data.context.replace("_", " ").title())
            op.node_tree = "{ntree}"
            op.node = "{node}"
            op.space = "{space}"
            op.region = "{region}"
            op.context = context.space_data.context.lower()
    
bpy.utils.register_class({idname})
registered_panels.append({idname})
"""
