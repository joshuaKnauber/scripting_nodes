import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ForLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ForLayoutNode"
    bl_label = "For Each - Layout"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_interface_input("For Each")
        self.add_list_input("List/Collection")

        self.add_dynamic_interface_output("Repeat")
        self.add_data_output("Element")
        self.add_integer_output("Index")

    def on_node_update(self):
        if len(self.inputs) == 2:
            if len(self.inputs[1].links):
                if self.inputs[1].links[0].from_socket.bl_idname == "SN_BlendDataSocket":
                    self.change_socket_type(self.inputs[1], "SN_BlendDataSocket").subtype = "COLLECTION"
                    self.change_socket_type(self.outputs["Element"], "SN_BlendDataSocket")
                else:
                    self.change_socket_type(self.inputs[1], "SN_ListSocket")
                    self.change_socket_type(self.outputs["Element"], "SN_DataSocket")
            else:
                self.change_socket_type(self.inputs[1], "SN_ListSocket")
                self.change_socket_type(self.outputs["Element"], "SN_DataSocket")


    def code_evaluate(self, context, touched_socket):

        if touched_socket == self.inputs[0]:
            return {
                "code": f"""
                        for_node_{self.uid} = 0
                        for_node_index_{self.uid} = 0
                        for for_node_index_{self.uid}, for_node_{self.uid} in enumerate({self.inputs[1].code()}):
                            {self.outputs["Repeat"].by_name(7) if self.outputs["Repeat"].by_name() else "pass"}
                        """
            }

        elif touched_socket == self.outputs["Element"]:
            return {"code": f"""for_node_{self.uid}"""}
        elif touched_socket == self.outputs["Index"]:
            return {"code": f"""for_node_index_{self.uid}"""}