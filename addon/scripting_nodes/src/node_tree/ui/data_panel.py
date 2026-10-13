import bpy
from ..editor import in_sn_tree
from ...core.references import target_label, users
from ...lib.trees import (
    scripting_node_trees,
    sn_nodes,
)
from ...nodes._reference_types import (
    PROPERTY_GROUP_NODES,
    PROPERTY_NODES,
    VARIABLE_NODES,
)
from ...nodes.base_node import draw_users
from ...sockets.socket_types import DATA_SOCKET_ICONS

# Icons for property types (mapped from socket icons)
PROPERTY_ICONS = {
    "SNA_Node_BoolProperty": DATA_SOCKET_ICONS["ScriptingBooleanSocket"],
    "SNA_Node_IntProperty": DATA_SOCKET_ICONS["ScriptingIntegerSocket"],
    "SNA_Node_FloatProperty": DATA_SOCKET_ICONS["ScriptingFloatSocket"],
    "SNA_Node_StringProperty": DATA_SOCKET_ICONS["ScriptingStringSocket"],
    "SNA_Node_FloatVectorProperty": "ORIENTATION_GLOBAL",
    "SNA_Node_EnumProperty": "PRESET",
    "SNA_Node_PointerProperty": "OBJECT_DATAMODE",
    "SNA_Node_CollectionProperty": "OUTLINER_COLLECTION",
    "SNA_Node_PropertyGroup": "OUTLINER_DATA_POINTCLOUD",
}

# Icons for variable types
VARIABLE_ICONS = {
    "SNA_Node_GlobalVariable": "WORLD",
    "SNA_Node_LocalVariable": "DOT",
}


def _draw_node_list(layout, context, types, icons):
    """One row per node of `types` in any tree: jump button, tree, use count."""
    search = context.scene.sna.ui.data_filter.lower()
    nodes = [
        node
        for tree in scripting_node_trees()
        for node in sn_nodes(tree)
        if node.bl_idname in types
    ]
    several_trees = len({node.id_data.name for node in nodes}) > 1
    col = layout.column(align=True)
    shown = 0
    for node in sorted(nodes, key=lambda n: (n.id_data.name, target_label(n).lower())):
        label = target_label(node)
        if search and search not in label.lower():
            continue
        shown += 1
        row = col.row(align=True)
        op = row.operator(
            "sna.go_to_node",
            text=label,
            icon=icons.get(node.bl_idname, "NODE"),
            emboss=False,
        )
        op.node_id = node.id
        sub = row.row(align=True)
        sub.alignment = "RIGHT"
        if several_trees:
            sub.label(text=node.id_data.name)
        sub.label(text=f"({len(users(node))})")
    if not shown:
        col.label(text="None")


class SNA_PT_Data(bpy.types.Panel):
    bl_idname = "SNA_PT_Data"
    bl_label = "Addon Data"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        self.layout.prop(context.scene.sna.ui, "data_filter", text="", icon="VIEWZOOM")


class SNA_PT_DataProperties(bpy.types.Panel):
    bl_idname = "SNA_PT_DataProperties"
    bl_label = "Properties"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_parent_id = "SNA_PT_Data"

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        types = PROPERTY_NODES + PROPERTY_GROUP_NODES
        _draw_node_list(self.layout, context, types, PROPERTY_ICONS)


class SNA_PT_DataVariables(bpy.types.Panel):
    bl_idname = "SNA_PT_DataVariables"
    bl_label = "Variables"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_parent_id = "SNA_PT_Data"

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        _draw_node_list(self.layout, context, VARIABLE_NODES, VARIABLE_ICONS)


def _count_group_interface(tree):
    """Return (param_count, return_count) for a group tree."""
    in_count = 0
    out_count = 0
    for node in tree.nodes:
        if node.bl_idname == "SNA_Node_GroupInput":
            in_count = len(node.get_items())
        elif node.bl_idname == "SNA_Node_GroupOutput":
            out_count = len(node.get_items())
    return in_count, out_count


class SNA_UL_FunctionsList(bpy.types.UIList):
    bl_idname = "SNA_UL_FunctionsList"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        # item is a NodeTree from bpy.data.node_groups
        in_count, out_count = _count_group_interface(item)
        ref_count = len(users(item))

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.label(text=item.name, icon="NODETREE")
            sub = row.row()
            sub.alignment = "RIGHT"
            sub.label(text=f"in:{in_count} out:{out_count}")
            sub.label(text=f"({ref_count})")
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text=item.name, icon="NODETREE")

    def filter_items(self, context, data, propname):
        trees = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item] * len(trees)
        for i, tree in enumerate(trees):
            if not (getattr(tree, "is_sn", False) and getattr(tree, "is_group", False)):
                flt_flags[i] = 0
        return flt_flags, []


class SNA_PT_DataFunctions(bpy.types.Panel):
    bl_idname = "SNA_PT_DataFunctions"
    bl_label = "Functions"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_parent_id = "SNA_PT_Data"

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        layout = self.layout
        sna = context.scene.sna

        row = layout.row()
        row.template_list(
            "SNA_UL_FunctionsList",
            "",
            bpy.data,
            "node_groups",
            sna.ui,
            "active_function_index",
            rows=4,
        )

        # Show the nodes that call the active function
        if 0 <= sna.ui.active_function_index < len(bpy.data.node_groups):
            tree = bpy.data.node_groups[sna.ui.active_function_index]
            if getattr(tree, "is_sn", False) and getattr(tree, "is_group", False):
                draw_users(layout, tree)
