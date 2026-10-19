import bpy
from ..editor import in_sn_tree
from ...core import functions
from ...core.references import target_label, users
from ...lib.trees import (
    scripting_node_trees,
    sn_nodes,
)
from ...nodes._reference_types import VARIABLE_NODES
from ...settings.assets import draw_assets
from ...settings.properties import draw_list, draw_settings

# Icons for variable types
VARIABLE_ICONS = {
    "SNA_Node_GlobalVariable": "WORLD",
    "SNA_Node_LocalVariable": "DOT",
}


def _draw_node_list(layout, types, icons):
    """One row per node of `types` in any tree: jump button, tree, use count."""
    nodes = [
        node
        for tree in scripting_node_trees()
        for node in sn_nodes(tree)
        if node.bl_idname in types
    ]
    several_trees = len({node.id_data.name for node in nodes}) > 1
    col = layout.column(align=True)
    for node in sorted(nodes, key=lambda n: (n.id_data.name, target_label(n).lower())):
        row = col.row(align=True)
        op = row.operator(
            "sna.go_to_node",
            text=target_label(node),
            icon=icons.get(node.bl_idname, "NODE"),
            emboss=False,
        )
        op.node_id = node.id
        sub = row.row(align=True)
        sub.alignment = "RIGHT"
        if several_trees:
            sub.label(text=node.id_data.name)
        sub.label(text=f"({len(users(node))})")
    if not nodes:
        col.label(text="None")


class SNA_PT_Data(bpy.types.Panel):
    bl_idname = "SNA_PT_Data"
    bl_label = "Addon Data"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        pass


class SNA_PT_DataProperties(bpy.types.Panel):
    bl_idname = "SNA_PT_DataProperties"
    bl_order = 0
    bl_label = "Properties"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_parent_id = "SNA_PT_Data"

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        layout = self.layout
        prop = draw_list(layout, "ADDON")
        if prop is None:
            return
        draw_settings(layout.column(), prop, top_level=True)
        users = [
            node
            for tree in scripting_node_trees()
            for node in sn_nodes(tree)
            if prop.id and getattr(node, "prop_id", "") == prop.id
        ]
        if users:
            box = layout.box()
            col = box.column(align=True)
            for node in users:
                row = col.row(align=True)
                row.label(text=node.bl_label, icon="NODE")
                row.label(text=f"[{node.id_data.name}]")
                op = row.operator("sna.go_to_node", text="", icon="VIEWZOOM")
                op.node_id = node.id


class SNA_PT_DataVariables(bpy.types.Panel):
    bl_idname = "SNA_PT_DataVariables"
    bl_order = 1
    bl_label = "Variables"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_parent_id = "SNA_PT_Data"

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        _draw_node_list(self.layout, VARIABLE_NODES, VARIABLE_ICONS)


def _draw_group_callers(layout, group_tree):
    """List the Group nodes that call this function."""
    callers = functions.callers(group_tree)
    if not callers:
        return
    box = layout.box()
    col = box.column(align=True)
    for node in callers:
        row = col.row(align=True)
        row.label(text=node.bl_label, icon="NODE")
        row.label(text=f"[{node.id_data.name}]")
        op = row.operator("sna.go_to_node", text="", icon="VIEWZOOM")
        op.node_id = node.id


class SNA_UL_FunctionsList(bpy.types.UIList):
    bl_idname = "SNA_UL_FunctionsList"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        # item is a NodeTree from bpy.data.node_groups
        in_count = len(functions.sockets(item, "INPUT"))
        out_count = len(functions.sockets(item, "OUTPUT"))
        ref_count = len(functions.callers(item))

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
            if not (getattr(tree, "is_sn", False) and tree.is_function):
                flt_flags[i] = 0
        return flt_flags, []


class SNA_PT_DataFunctions(bpy.types.Panel):
    bl_idname = "SNA_PT_DataFunctions"
    bl_order = 2
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

        # Show the Call Group nodes that reference the active function
        if 0 <= sna.ui.active_function_index < len(bpy.data.node_groups):
            tree = bpy.data.node_groups[sna.ui.active_function_index]
            if getattr(tree, "is_sn", False) and tree.is_function:
                _draw_group_callers(layout, tree)


class SNA_PT_DataAssets(bpy.types.Panel):
    bl_idname = "SNA_PT_DataAssets"
    bl_order = 3
    bl_label = "Assets"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_parent_id = "SNA_PT_Data"

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        draw_assets(self.layout, context)
