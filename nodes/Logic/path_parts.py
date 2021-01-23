import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_PathPartsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PathPartsNode"
    bl_label = "Path Components"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_string_input("Path").subtype = "FILE"
        self.add_string_output("Directory").subtype = "DIRECTORY"
        self.add_string_output("File Name")
        self.add_list_output("Path Parts")


    def code_evaluate(self, context, touched_socket):
        
        if touched_socket == self.outputs["Directory"]:
            return {
                "code": f"""os.path.dirname({self.inputs[0].code()})"""
            }
        elif touched_socket == self.outputs["File Name"]:
            return {
                "code": f"""os.path.basename({self.inputs[0].code()})"""
            }
        elif touched_socket == self.outputs["Path Parts"]:
            return {
                "code": f"""os.path.normpath({self.inputs[0].code()}).split(os.path.sep)"""
            }