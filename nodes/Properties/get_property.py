import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



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
            self.report({"WARNING"},message="Right-Click any property and click 'Copy Property' to get a correct property")
        return {"FINISHED"}




class SN_GetPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetPropertyNode"
    bl_label = "Get Property"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
        
    def get_details(self):
        try:
            path_details = json.loads(self.copied_path)
            return path_details
        except:
            return None
                         
                
    def get_copied(self,context):
        if self.copied_path:
            path_details = self.get_details()
            if path_details:
                pass
    
    
    copied_path: bpy.props.StringProperty(update=get_copied)
    
    
    def reset_node(self):
        self.copied_path = ""
        self.inputs.clear()
        self.outputs.clear()
    
    
    def on_copy(self,node):
        self.reset_node()
        

    def draw_node(self,context,layout):
        if not self.copied_path:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("sn.paste_property_path",text="Paste Property",icon="PASTEDOWN").node = self.name
    

    def code_evaluate(self, context, touched_socket):
        return {
            "code": f"""
                    """
        }