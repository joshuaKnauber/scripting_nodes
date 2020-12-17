import bpy
from textwrap import wrap



class SN_SelectNode(bpy.types.Operator):
    bl_idname = "sn.select_node"
    bl_label = "Select Node"
    bl_description = "Selects this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()
    node_tree: bpy.props.StringProperty()

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        if self.node_tree in addon_tree.sn_graphs:
            if self.node in addon_tree.sn_graphs[self.node_tree].node_tree.nodes:
                for node in addon_tree.sn_graphs[self.node_tree].node_tree.nodes:
                    node.select = False
                node = addon_tree.sn_graphs[self.node_tree].node_tree.nodes[self.node]
                addon_tree.sn_graphs[self.node_tree].node_tree.nodes.active = node
                node.select = True
                addon_tree.sn_graph_index = addon_tree.sn_graphs.find(self.node_tree)
                bpy.ops.node.view_selected("INVOKE_DEFAULT")
        return {"FINISHED"}




class SN_PT_AddonErrorPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonErrorPanel"
    bl_label = "Errors"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 3

    @classmethod
    def poll(cls, context):
        if context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree":
            return len(context.scene.sn.addon_tree().sn_graphs[0].errors) > 0
        return False
    
    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.sn,"show_char_control",text="",emboss=False,icon="PREFERENCES")
        
    def char_amount(self, context):
        return int(context.area.regions[1].width // 16 * context.scene.sn.chars_per_line/10)

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        addon_graph = addon_tree.sn_graphs[0]
        
        if context.scene.sn.show_char_control:
            layout.prop(context.scene.sn, "chars_per_line",text="Line Wrap")
        
        for error in addon_graph.errors:
            box = layout.box()
            row = box.row()
            col = row.column()
            col.alert = error.fatal
            col.label(text=error.title)
            op = row.operator("sn.select_node",text="",emboss=False,icon="RESTRICT_SELECT_OFF")
            op.node = error.node
            op.node_tree = error.node_tree
            col = box.column(align=True)
            col.enabled = False
            for line in wrap(error.description, self.char_amount(context)):
                col.label(text=line)