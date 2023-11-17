import bpy

from ....utils.nodes import get_node_by_id


_REGISTERED = {}  # {node_id: [panel_idname, ...]}


class SNA_OT_Picker(bpy.types.Operator):
    bl_idname = "sna.picker"
    bl_label = "Location Picker"
    bl_description = "Pick a location in the interface"
    bl_options = {"REGISTER", "UNDO"}

    locations: bpy.props.EnumProperty(
        items=[
            ("PANEL_LOCATIONS", "Panel Locations", "Panel Locations"),
            ("PANELS", "Panels", "Panels"),
            ("MENUS", "Menus", "Menus"),
        ]
    )

    node: bpy.props.StringProperty()

    def execute(self, context):
        if self.locations == "PANELS":
            register_panels(self.node)
        return {"FINISHED"}


class SNA_OT_Pick(bpy.types.Operator):
    bl_idname = "sna.pick"
    bl_label = "Picker"
    bl_description = "Pick this location in the interface"
    bl_options = {"REGISTER", "UNDO"}

    space: bpy.props.StringProperty()
    region: bpy.props.StringProperty()
    category: bpy.props.StringProperty()
    context: bpy.props.StringProperty()

    node: bpy.props.StringProperty()

    def execute(self, context):
        # unregister the old panels
        global _REGISTERED
        if self.node in _REGISTERED:
            for panel in _REGISTERED[self.node]:
                try:
                    exec(f"bpy.utils.unregister_class(bpy.types.{panel})")
                except Exception as e:
                    pass
            del _REGISTERED[self.node]
        # set the values
        node = get_node_by_id(self.node)
        node.space = self.space
        node.region = self.region
        node.category = self.category
        node.context = self.context
        return {"FINISHED"}


def register_panels(node: str):
    global _REGISTERED
    spaces = get_space_types()
    regions = get_region_types()
    categories = get_panel_categories()
    for space in spaces:
        for region in regions:
            cats = [*categories.get(space, {}).get(region, {})]
            if not "Scripting Nodes" in cats:
                cats.append("Scripting Nodes")
            for i, category in enumerate(cats):
                idname = f"SNA_PT_{space}_{region}_{i}"
                try:
                    exec(PANEL_TEMPLATE(node, idname, space, region, category))
                    if not node in _REGISTERED:
                        _REGISTERED[node] = []
                    _REGISTERED[node].append(idname)
                except Exception as e:
                    pass


def get_space_types():
    return bpy.types.Panel.bl_rna.properties["bl_space_type"].enum_items.keys()


def get_region_types():
    return bpy.types.Panel.bl_rna.properties["bl_region_type"].enum_items.keys()


def get_panel_categories():
    categories = {}
    for cls in bpy.types.Panel.__subclasses__():
        if getattr(cls, "bl_category", None):
            if cls.bl_space_type not in categories:
                categories[cls.bl_space_type] = {}
            if cls.bl_region_type not in categories[cls.bl_space_type]:
                categories[cls.bl_space_type][cls.bl_region_type] = set()
            categories[cls.bl_space_type][cls.bl_region_type].add(cls.bl_category)
    return categories


def PANEL_TEMPLATE(node: str, idname, space, region, category=""):
    return f"""
class {idname}(bpy.types.Panel):
    bl_label = "Picker"
    bl_space_type = '{space}'
    bl_region_type = '{region}'
    bl_category = '{category if category else "Scripting Nodes"}'
    bl_options = {{"HIDE_HEADER"}}
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.alert = True
        row = col.row(align=True)
        row.scale_y = 2
        op = row.operator(
            "sna.pick", text="Select {region.replace("_", " ").title()} region in {space.replace("_", " ").title()}", icon="RESTRICT_SELECT_OFF")
        op.node = "{node}"
        op.space = "{space}"
        op.region = "{region}"
        op.category = "{category}"
        op.context = ""
        if hasattr(context.space_data, "context"):
            row = col.row(align=True)
            row.scale_y = 1.25
            op = row.operator("sna.pick", text=f"Select with context '{{context.space_data.context.title()}}'",
                         icon="RESTRICT_SELECT_OFF")
            op.node = "{node}"
            op.space = "{space}"
            op.region = "{region}"
            op.category = "{category}"
            op.context = context.space_data.context.lower()

bpy.utils.register_class({idname})
"""
