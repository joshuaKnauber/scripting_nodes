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
    
    
    
class SN_OT_AddBlenderPropertyNode(bpy.types.Operator):
    bl_idname = "sn.add_blend_property"
    bl_label = "Add Blender Property Node"
    bl_description = "Adds a blender property node and pastes the filepath if available"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_BlenderPropertyNode", use_transform=True)
        node = context.space_data.node_tree.nodes.active
        if "bpy." in context.window_manager.clipboard and not ".ops." in context.window_manager.clipboard:
            bpy.ops.sn.paste_data_path(node=node.name, node_tree=context.space_data.node_tree.name)
        return {"FINISHED"}
