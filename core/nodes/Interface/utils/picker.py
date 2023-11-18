import bpy

from .....utils.redraw import redraw
from ....utils.nodes import get_node_by_id


_PICKER_ACTIVE = False
_REGISTERED = []


class SNA_OT_Picker(bpy.types.Operator):
    bl_idname = "sna.picker"
    bl_label = "Location Picker"
    bl_description = "Pick a location in the interface"
    bl_options = {"REGISTER", "UNDO"}

    locations: bpy.props.EnumProperty(
        items=[
            ("SUBPANELS", "Subpanels", "Subpanels"),
            ("PANELS", "Panels", "Panels"),
            ("MENUS", "Menus", "Menus"),
        ]
    )

    node: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        global _PICKER_ACTIVE
        return not _PICKER_ACTIVE

    def execute(self, context):
        global _PICKER_ACTIVE
        _PICKER_ACTIVE = True
        if self.locations == "PANELS":
            register_panels(self.node)
        elif self.locations == "SUBPANELS":
            add_to_panels(self.node)
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

    idname: bpy.props.StringProperty()

    node: bpy.props.StringProperty()

    def populate_panel(self):
        # unregister the old panels
        global _REGISTERED
        for panel in _REGISTERED:
            try:
                bpy.utils.unregister_class(panel)
            except Exception as e:
                pass
        _REGISTERED = []
        # set the values
        node = get_node_by_id(self.node)
        node.space = self.space
        node.region = self.region
        node.category = self.category
        node.context = self.context

    def populate_subpanel(self):
        # unregister the old panels
        global _REGISTERED
        for panel in _REGISTERED:
            try:
                panel[1].remove(panel[0])
            except Exception as e:
                pass
        _REGISTERED = []
        # set the values
        node = get_node_by_id(self.node)
        node.blender_panel = self.idname
        node.blender_space = self.space
        node.blender_region = self.region
        node.blender_category = self.category
        node.blender_context = self.context

    def execute(self, context):
        global _PICKER_ACTIVE
        _PICKER_ACTIVE = False
        if self.idname:
            self.populate_subpanel()
        else:
            self.populate_panel()
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
                    exec(
                        PANEL_TEMPLATE(node, idname, space, region, category), globals()
                    )
                except Exception as e:
                    pass
    redraw(True)


def add_to_panels(node: str):
    global _REGISTERED
    panels = get_panels()
    names = set()
    for panel in panels:
        if not hasattr(panel, "bl_parent_id") and panel.__name__ not in names:
            try:
                exec(
                    ADD_TO_PANEL_TEMPLATE(node, f"draw_{panel.__name__}", panel),
                    globals(),
                )
                _REGISTERED[-1][1] = panel
                names.add(panel.__name__)
            except Exception as e:
                pass
    redraw(True)


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


def get_panels():
    return bpy.types.Panel.__subclasses__()


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
        op.idname = ""
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
            op.idname = ""

bpy.utils.register_class({idname})
_REGISTERED.append({idname})
"""


def ADD_TO_PANEL_TEMPLATE(node: str, name: str, panel: bpy.types.Panel):
    return f"""
def {name}(self, context):
    row = self.layout.row()
    row.alert = True
    row.scale_y = 2
    op = row.operator(
        "sna.pick", text="Select Panel", icon="RESTRICT_SELECT_OFF")
    op.node = "{node}"
    op.idname = "{panel.__name__}"
    op.space = "{panel.bl_space_type}"
    op.region = "{panel.bl_region_type}"
    op.category = "{getattr(panel, "bl_category", "")}"
    op.context = "{getattr(panel, "bl_context", "")}"

bpy.types.{panel.__name__}.append({name})
_REGISTERED.append([{name}, None])
"""
