import bpy


class SN_OT_OpenNodeDocs(bpy.types.Operator):
    bl_idname = "sn.open_node_docs"
    bl_label = "Open Node Docs"
    bl_description = "Open Node Documentation"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        if getattr(context.space_data.node_tree.nodes.active, "is_sn", False):
            if context.space_data.node_tree.nodes.active.select:
                bpy.ops.wm.url_open(url="https://joshuaknauber.notion.site/555efb921f50426ea4d5812f1aa3e462?v=d781b590cc8f47449cb20812deab0cc6")
        return {"FINISHED"}
    
    
    
class SN_MT_AddOperatorMenu(bpy.types.Menu):
    bl_idname = "SN_MT_AddOperatorMenu"
    bl_label = "Add Operator Node"

    def draw(self, context):
        layout = self.layout.menu_pie()
        layout.operator("sn.add_copied_operator_node", text="Run Operator", icon="POSE_HLT").is_button = False
        layout.operator("sn.add_copied_operator_node", text="Button", icon="MOUSE_LMB").is_button = True
    
    
class SN_OT_AddCopiedNode(bpy.types.Operator):
    bl_idname = "sn.add_copied_node"
    bl_label = "Add Copied Node"
    bl_description = "Adds a node from the copied path for operators and properties"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        if "bpy." in context.window_manager.clipboard and ".ops." in context.window_manager.clipboard:
            bpy.ops.wm.call_menu_pie(name="SN_MT_AddOperatorMenu")
        elif "bpy." in context.window_manager.clipboard and not ".ops." in context.window_manager.clipboard:
            bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_BlenderPropertyNode", use_transform=True)
            node = context.space_data.node_tree.nodes.active
            bpy.ops.sn.paste_data_path(node=node.name, node_tree=context.space_data.node_tree.name)
        return {"FINISHED"}
    
    
class SN_OT_AddCopiedOperatorNode(bpy.types.Operator):
    bl_idname = "sn.add_copied_operator_node"
    bl_label = "Add Copied Operator Node"
    bl_description = "Adds a node from the copied path for operators"
    bl_options = {"REGISTER", "INTERNAL"}
    
    is_button: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        if "bpy." in context.window_manager.clipboard and ".ops." in context.window_manager.clipboard:
            if self.is_button:
                bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_ButtonNodeNew", use_transform=True)
            else:
                bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_RunOperatorNode", use_transform=True)
            node = context.space_data.node_tree.nodes.active
            node.source_type = "BLENDER"
            node.pasted_operator = context.window_manager.clipboard
        return {"FINISHED"}