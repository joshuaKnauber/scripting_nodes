import bpy
from ....lib.editor.editor import in_sn_tree
from ....lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
    sn_nodes,
)
from ...sockets.socket_types import DATA_SOCKET_ICONS

# Node type identifiers for properties and variables
PROPERTY_NODE_TYPES = {
    "SNA_Node_BoolProperty",
    "SNA_Node_IntProperty",
    "SNA_Node_FloatProperty",
    "SNA_Node_StringProperty",
    "SNA_Node_CollectionProperty",
}

VARIABLE_NODE_TYPES = {
    "SNA_Node_GlobalVariable",
    "SNA_Node_LocalVariable",
}

# Icons for property types (mapped from socket icons)
PROPERTY_ICONS = {
    "SNA_Node_BoolProperty": DATA_SOCKET_ICONS["ScriptingBooleanSocket"],
    "SNA_Node_IntProperty": DATA_SOCKET_ICONS["ScriptingIntegerSocket"],
    "SNA_Node_FloatProperty": DATA_SOCKET_ICONS["ScriptingFloatSocket"],
    "SNA_Node_StringProperty": DATA_SOCKET_ICONS["ScriptingStringSocket"],
    "SNA_Node_CollectionProperty": "OUTLINER_COLLECTION",
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


def get_selected_reference(sna, node_types, index):
    """Get the selected reference from the list by index into the full references collection"""
    # The index is into the full references collection, not the filtered one
    if 0 <= index < len(sna.references):
        ref = sna.references[index]
        # Check if it's the right type
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


class SNA_UL_PropertyNodesList(bpy.types.UIList):
    bl_idname = "SNA_UL_PropertyNodesList"

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        node = item.node
        if not node:
            layout.label(text="(Missing)", icon="ERROR")
            return

        # Get property label (prop_label) and type icon
        label = getattr(node, "prop_label", "") or node.bl_label
        type_icon = PROPERTY_ICONS.get(node.bl_idname, "NODE")
        tree_name = node.id_data.name
        ref_count = get_reference_count(item.name)

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.label(text=label, icon=type_icon)
            sub = row.row()
            sub.alignment = "RIGHT"
            sub.label(text=f"({ref_count})")
            sub.label(text=f"[{tree_name}]")
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text=label, icon=type_icon)

    def filter_items(self, context, data, propname):
        references = getattr(data, propname)

        flt_flags = [self.bitflag_filter_item] * len(references)
        flt_neworder = []

        # Filter to only show property nodes
        for i, ref in enumerate(references):
            node = ref.node
            if not node or node.bl_idname not in PROPERTY_NODE_TYPES:
                flt_flags[i] = 0

        return flt_flags, flt_neworder


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
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        pass


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
        layout = self.layout
        sna = context.scene.sna

        row = layout.row()
        row.template_list(
            "SNA_UL_PropertyNodesList",
            "",
            sna,
            "references",
            sna.ui,
            "active_property_index",
            rows=4,
        )

        # Show referencing nodes for selected property
        ref = get_selected_reference(
            sna, PROPERTY_NODE_TYPES, sna.ui.active_property_index
        )
        if ref and ref.node:
            draw_referencing_nodes(layout, ref.name)


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
        layout = self.layout
        sna = context.scene.sna

        row = layout.row()
        row.template_list(
            "SNA_UL_VariableNodesList",
            "",
            sna,
            "references",
            sna.ui,
            "active_variable_index",
            rows=4,
        )

        # Show referencing nodes for selected variable
        ref = get_selected_reference(
            sna, VARIABLE_NODE_TYPES, sna.ui.active_variable_index
        )
        if ref and ref.node:
            draw_referencing_nodes(layout, ref.name)
