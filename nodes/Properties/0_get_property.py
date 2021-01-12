import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup


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
        
        
    def get_path_end(self):
        path_end = ""
        for part in self.get_details()["path_parts"]:
            if type(part) == dict:
                path_end = ""
            elif path_end:
                path_end += "." + part                         
            else:
                path_end += part
        return path_end########### numerics
    
                
    def get_copied(self,context):
        if self.copied_path:
            path_details = self.get_details()
            if path_details:
                # setup_sockets(self, path_details)
                out = self.add_output_from_type(path_details["prop_type"],path_details["prop_name"],path_details["prop_array_length"])
                if hasattr(out,"is_color"):
                    out.is_color = path_details["is_color"]
        else:
            self.reset_node()

    
    copied_path: bpy.props.StringProperty(update=get_copied)
    
    
    def reset_node(self):
        self.inputs.clear()
        self.outputs.clear()
        

    def draw_node(self,context,layout):
        if not self.copied_path:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("sn.paste_property_path",text="Paste Property",icon="PASTEDOWN").node = self.name
        else:
            layout.operator("sn.reset_node",icon="UNLINKED").node = self.name
    

    def code_evaluate(self, context, touched_socket):
        return {
            "code": f"{self.inputs[0].code()}.{self.get_path_end()}"
        }