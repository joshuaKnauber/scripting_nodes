import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ForProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ForProgramNode"
    bl_label = "For Each - Program"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_execute_input("For Each")
        self.add_blend_data_input("Collection / List").subtype = "COLLECTION"

        self.add_execute_output("Continue")
        self.add_execute_output("Repeat")
        self.add_blend_data_output("Element")
        self.add_integer_output("Index")

    def on_link_insert(self, link):
        if link.to_socket == self.inputs[1]:
            if link.from_socket.bl_idname == "SN_BlendDataSocket" and link.from_socket.subtype == "COLLECTION":
                if self.inputs[1].bl_idname != "SN_BlendDataSocket":
                    self.change_socket_type(self.inputs[1], "SN_BlendDataSocket").subtype = "COLLECTION"
                    self.change_socket_type(self.outputs[2], "SN_BlendDataSocket")
                self.inputs[1].default_text = "Collection"

                self.outputs[2].data_type = link.from_socket.data_type
                self.outputs[2].data_name = link.from_socket.data_name
                for link in self.outputs[2].links:
                    link.to_socket.node.on_link_insert(link)

            else:
                self.change_socket_type(self.inputs[1], "SN_ListSocket")
                self.change_socket_type(self.outputs[2], "SN_DataSocket")

                if link.from_socket.bl_idname == "SN_ListSocket":
                    self.inputs[1].default_text = "List"
                else:
                    self.inputs[1].default_text = "Collection / List"

    def code_evaluate(self, context, touched_socket):

        if touched_socket == self.inputs[0]:
            if not self.inputs[1].links:
                self.add_error("No input", "Nothing is connected to this for node")
            return {
                "code": f"""
                        for_node_{self.uid} = 0
                        for_node_index_{self.uid} = 0
                        for for_node_index_{self.uid}, for_node_{self.uid} in enumerate({self.inputs[1].code()}):
                            {self.outputs[1].code(7) if self.outputs[1].code() else "pass"}
                        {self.outputs[0].code(6)}
                        """
            }

        elif touched_socket == self.outputs[2]:
            if self.inputs[0].links:
                return {"code": f"""for_node_{self.uid}"""}
            return {"code": "None"}
        elif touched_socket == self.outputs[3]:
            if self.inputs[0].links:
                return {"code": f"""for_node_index_{self.uid}"""}
            return {"code": "0"}