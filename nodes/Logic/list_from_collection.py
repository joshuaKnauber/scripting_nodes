import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ListFromCollectionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ListFromCollectionNode"
    bl_label = "List from Collection"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").subtype = "COLLECTION"
        self.add_list_output("List")


    def code_evaluate(self, context, touched_socket):
        return {
            "code": f"""list({self.inputs[0].code()})"""
        }