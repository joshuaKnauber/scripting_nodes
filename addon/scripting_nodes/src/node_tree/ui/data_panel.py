import bpy
from ..editor import in_sn_tree
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
        col.label(text="Add a Global or Local Variable node", icon="INFO")


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
            draw_used_by(layout, users)


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


def draw_used_by(layout, nodes):
    """The nodes using something, with jump buttons."""
    col = layout.box().column(align=True)
    col.label(text="Used by")
    for node in nodes:
        row = col.row(align=True)
        name = node.label or getattr(node, "draw_label", lambda: node.name)()
        row.label(text=f"{name} ({node.id_data.name})", icon="NODE")
        op = row.operator("sna.go_to_node", text="", icon="VIEWZOOM", emboss=False)
        op.node_id = node.id


class SNA_PT_DataAssets(bpy.types.Panel):
    bl_idname = "SNA_PT_DataAssets"
    bl_order = 2
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
