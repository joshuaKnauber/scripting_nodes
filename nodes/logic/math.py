#SN_MathNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_MathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MathNode"
    bl_label = "Math"
    bl_icon = "CON_TRANSLIKE"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>do math operations</>."
                ""],
        "python": ["<number>8</> * <number>4</>"]

    }

    operation: bpy.props.EnumProperty(items=[("+", "Add", "Add two numbers"), ("-", "Subtract", "Subtract two numbers"), ("*", "Multiply", "Multiply two numbers"), ("/", "Divide", "Divide two numbers")],name="Operation", description="The operation you want to commence")

    def inititialize(self,context):
        self.sockets.create_input(self,"FLOAT","Value")
        self.sockets.create_input(self,"FLOAT","Value")
        self.sockets.create_output(self,"FLOAT","Output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

    def update(self):
        if len(self.inputs) == 2 and len(self.outputs):
            if len(self.inputs[0].links):
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_IntSocket" and not self.outputs[0].bl_idname == "SN_IntSocket":
                    self.sockets.change_socket_type(self, self.inputs[0], "INTEGER")
                    self.sockets.change_socket_type(self, self.inputs[1], "INTEGER")
                    self.sockets.change_socket_type(self, self.outputs[0], "INTEGER")
            if len(self.inputs[1].links):
                if self.inputs[1].links[0].from_socket.bl_idname == "SN_IntSocket" and not self.outputs[0].bl_idname == "SN_IntSocket":
                    self.sockets.change_socket_type(self, self.inputs[0], "INTEGER")
                    self.sockets.change_socket_type(self, self.inputs[1], "INTEGER")
                    self.sockets.change_socket_type(self, self.outputs[0], "INTEGER")
            if not len(self.inputs[0].links) and not len(self.inputs[1].links) and not self.outputs[0].bl_idname == "SN_FloatSocket":
                self.sockets.change_socket_type(self, self.inputs[0], "FLOAT")
                self.sockets.change_socket_type(self, self.inputs[1], "FLOAT")
                self.sockets.change_socket_type(self, self.outputs[0], "FLOAT")

        self.update_socket_connections()
        self.update_vector_sockets()
        self.update_dynamic(True)
        self.update_dynamic(False)

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["(", node_data["input_data"][0]["code"], self.operation, node_data["input_data"][1]["code"], ")"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
