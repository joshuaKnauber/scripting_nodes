#SN_ForProgramNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ForProgramNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_ForProgramNode"
    bl_label = "For (Program)"
    bl_icon = "CON_ACTION"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    def reset_data_type(self, context):
        if self.inputs[1].links[0].from_socket.bl_idname in ["SN_CollectionSocket", "SN_ObjectSocket"]:
            if self.outputs[2].is_linked:
                if self.outputs[2].links[0].to_socket.bl_idname in ["SN_CollectionSocket", "SN_ObjectSocket"]:
                    self.outputs[2].links[0].to_node.reset_data_type(None)
            else:
                self.update()

    def inititialize(self,context):
        self.var_name = self.get_var_name()
        self.index_name = "for_execute_node_index_" + self.var_name.split("_")[-1]

        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"COLLECTION","Input")

        self.sockets.create_output(self,"EXECUTE","Execute")
        self.sockets.create_output(self,"EXECUTE","Repeat")
        self.sockets.create_output(self,"OBJECT","Element")
        self.sockets.create_output(self,"INTEGER","Index")

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "for_execute_node_"+str(highest_var_name + 1)

    var_name: bpy.props.StringProperty(default="for_execute_node_0")
    index_name: bpy.props.StringProperty(default="for_execute_node_index_0")

    def copy(self, node):
        self.var_name = self.get_var_name()
        self.index_name = "for_execute_node_index_" + self.var_name.split("_")[-1]

    def draw_buttons(self, context, layout):
        if len(self.inputs[1].links) == 1:
            if self.inputs[1].links[0].from_socket.bl_idname == "SN_CollectionSocket":
                data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                if data_type != "":
                    box = layout.box()
                    box.label(text=eval(data_type).bl_rna.name)

    def evaluate(self, socket, node_data, errors):
        # return the name of the variable
        if socket == self.outputs[2]:
            return {"blocks": [{"lines": [[self.var_name]],"indented": []}],"errors": errors}
        if socket == self.outputs[3]:
            return {"blocks": [{"lines": [[self.index_name]],"indented": []}],"errors": errors}
        # return the code block and next output
        else:
            next_code = ""
            if node_data["output_data"][0]["code"]:
                next_code = node_data["output_data"][0]["code"]

            output = ""
            if node_data["output_data"][1]["code"]:
                output = node_data["output_data"][1]["code"]

            if output == "":
                output = "pass"
            return {
                "blocks": [
                    {
                        "lines": [ # lines is a list of lists, where the lists represent the different lines
                            [self.var_name + " = 0"],
                            [self.index_name + " = 0"],
                            ["for " + self.index_name + ", " + self.var_name + " in enumerate(", node_data["input_data"][1]["code"], "):"]
                        ],
                        "indented": [ # indented is a list of lists, where the lists represent the different lines
                            [output]
                        ]
                    },
                    {
                        "lines": [ # lines is a list of lists, where the lists represent the different lines
                            [next_code]
                        ],
                        "indented": [ # indented is a list of lists, where the lists represent the different lines
                        ]
                    }
                ],
                "errors": errors
            }

    def data_type(self, output):
        if len(self.inputs[1].links) == 1:
            if self.inputs[1].links[0].from_socket.bl_idname == "SN_CollectionSocket":
                data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                if data_type != "":
                    return data_type

        return ""

