import bpy
import json



class SN_PastePropertyPath(bpy.types.Operator):
    bl_idname = "sn.paste_property_path"
    bl_label = "Paste Property Path"
    bl_description = "Pastes your copies property path into this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()

    def execute(self, context):
        clipboard = bpy.context.window_manager.clipboard
        if "data_block" in clipboard and "identifier" in clipboard:
            context.space_data.node_tree.nodes[self.node].copied_path = clipboard
        else:
            self.report({"WARNING"},message="Right-Click any property and click 'Copy Property' to get a valid property")
        return {"FINISHED"}



class SN_ResetPropertyNode(bpy.types.Operator):
    bl_idname = "sn.reset_property_node"
    bl_label = "Reset Node"
    bl_description = "Resets this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        if hasattr(node,"copied_path"):
            node.copied_path = ""
        if hasattr(node,"operator"):
            node.operator = ""
        return {"FINISHED"}
    
    
    
def get_data(data):
    try:
        data = json.loads(data)
        return data
    except:
        return None



def setup_data_input(node, data):
    inp = node.add_blend_data_input(data["data_block"]["name"])
    inp.data_type = data["data_block"]["type"]
    inp.data_name = data["data_block"]["name"]

def setup_data_output(node, data):
    out = node.add_blend_data_output(data["data_block"]["name"])
    out.data_type = data["data_block"]["type"]
    out.data_name = data["data_block"]["name"]
