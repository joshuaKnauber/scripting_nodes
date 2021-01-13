import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ListInsertNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ListInsertNode"
    bl_label = "Insert in List"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_execute_input("Insert in List")
        self.add_execute_output("Execute")

        self.add_list_input("List")
        self.add_integer_input("Index")
        self.add_data_input("Value")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""
                    {self.inputs[1].code()}.insert({self.inputs[2].code()}, {self.inputs[3].code()})
                    {self.outputs[0].code(5)}
                    """
        }