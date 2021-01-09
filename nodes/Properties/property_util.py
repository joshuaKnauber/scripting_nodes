import bpy



class SN_PastePropertyPath(bpy.types.Operator):
    bl_idname = "sn.paste_property_path"
    bl_label = "Paste Property Path"
    bl_description = "Pastes your copies property path into this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()

    def execute(self, context):
        clipboard = bpy.context.window_manager.clipboard
        if "bpy." in clipboard and not ".ops." in clipboard:
            context.space_data.node_tree.nodes[self.node].copied_path = clipboard
        else:
            self.report({"WARNING"},message="Right-Click any property and click 'Copy Property' to get a valid property")
        return {"FINISHED"}



class SN_ResetNode(bpy.types.Operator):
    bl_idname = "sn.reset_node"
    bl_label = "Reset Node"
    bl_description = "Resets this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node].copied_path = ""
        return {"FINISHED"}



def setup_sockets(node,path_details):
    data_input = None
    for part in path_details["path_parts"]:
        if type(part) == dict:
            if part["is_numeric"]:
                node.add_integer_input(part["name"] + " Index").set_default(part["index"])
            else:
                data_input = part
    if data_input:
        inp = node.add_blend_data_input(data_input["name"])
        inp.data_type = data_input["data_type"]