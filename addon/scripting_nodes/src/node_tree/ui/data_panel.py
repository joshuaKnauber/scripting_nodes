import bpy
from ..editor import in_sn_tree
from ...core import functions
from ...lib.trees import (
    scripting_node_trees,
    sn_nodes,
)
from ...settings.properties import draw_list, draw_settings

VARIABLE_NODE_TYPES = {
    "SNA_Node_GlobalVariable",
    "SNA_Node_LocalVariable",
}

# Icons for variable types
VARIABLE_ICONS = {
    "SNA_Node_GlobalVariable": "WORLD",
    "SNA_Node_LocalVariable": "DOT",
}


def get_nodes_referencing(ref_name):
    """Find all nodes that reference a given property/variable by name"""
    referencing_nodes = []
    for ntree in scripting_node_trees():
        for node in sn_nodes(ntree):
            # Check if node has reference properties
            ref_props = getattr(node, "sn_reference_properties", None)
            if ref_props:
                for prop_name in ref_props:
                    if (
                        hasattr(node, prop_name)
                        and getattr(node, prop_name) == ref_name
                    ):
                        referencing_nodes.append(node)
                        break
    return referencing_nodes


def get_reference_count(ref_name):
    """Count how many nodes reference a given property/variable"""
    return len(get_nodes_referencing(ref_name))


def get_selected_reference(sna, collection_attr, node_types, index):
    """Return the selected reference from a per-signature collection by index."""
    coll = getattr(sna, collection_attr)
    if 0 <= index < len(coll):
        ref = coll[index]
        if ref.node and ref.node.bl_idname in node_types:
            return ref
    return None


def draw_referencing_nodes(layout, ref_name):
    """Draw the list of nodes that reference a property/variable"""
    referencing_nodes = get_nodes_referencing(ref_name)

    if not referencing_nodes:
        return

    box = layout.box()
    col = box.column(align=True)

    for node in referencing_nodes:
        row = col.row(align=True)
        row.label(text=node.bl_label, icon="NODE")
        row.label(text=f"[{node.id_data.name}]")
        op = row.operator("sna.go_to_node", text="", icon="VIEWZOOM")
        op.node_id = node.id


class SNA_UL_VariableNodesList(bpy.types.UIList):
    bl_idname = "SNA_UL_VariableNodesList"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        node = item.node
        if not node:
            layout.label(text="(Missing)", icon="ERROR")
            return

        # Get node name and type icon
        type_icon = VARIABLE_ICONS.get(node.bl_idname, "NODE")
        tree_name = node.id_data.name
        ref_count = get_reference_count(item.name)

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.label(text=node.name, icon=type_icon)
            sub = row.row()
            sub.alignment = "RIGHT"
            sub.label(text=f"({ref_count})")
            sub.label(text=f"[{tree_name}]")
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text=node.name, icon=type_icon)

    def filter_items(self, context, data, propname):
        references = getattr(data, propname)

        flt_flags = [self.bitflag_filter_item] * len(references)
        flt_neworder = []

        # Filter to only show variable nodes
        for i, ref in enumerate(references):
            node = ref.node
            if not node or node.bl_idname not in VARIABLE_NODE_TYPES:
                flt_flags[i] = 0

        return flt_flags, flt_neworder


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
        from ...settings.settings import DATA_PANEL_VARIABLES_ATTR

        layout = self.layout
        sna = context.scene.sna

        row = layout.row()
        row.template_list(
            "SNA_UL_VariableNodesList",
            "",
            sna,
            DATA_PANEL_VARIABLES_ATTR,
            sna.ui,
            "active_variable_index",
            rows=4,
        )

        # Show referencing nodes for selected variable
        ref = get_selected_reference(
            sna,
            DATA_PANEL_VARIABLES_ATTR,
            VARIABLE_NODE_TYPES,
            sna.ui.active_variable_index,
        )
        if ref and ref.node:
            draw_referencing_nodes(layout, ref.name)


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
