#SN_VectorMathNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_VectorMathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_VectorMathNode"
    bl_label = "Vector Math"
    bl_icon = "CON_TRANSLIKE"
    node_color = (0.65,0,0)
    should_be_registered = False

    def update_operation(self,context):
        if self.operation in ["ADD","SUBTRACT","CROSS_PRODUCT"]:
            if len(self.inputs) == 1:
                self.sockets.create_input(self,"VECTOR","Value")
            if self.outputs[0].bl_idname != "SN_VectorSocket":
                self.sockets.remove_output(self,self.outputs[0])
                self.sockets.create_output(self,"VECTOR","Output")
        elif self.operation in ["DOT_PRODUCT","DISTANCE"]:
            if len(self.inputs) == 1:
                self.sockets.create_input(self,"VECTOR","Value")
            if self.outputs[0].bl_idname == "SN_VectorSocket":
                self.sockets.remove_output(self,self.outputs[0])
                self.sockets.create_output(self,"FLOAT","Output")
        elif self.operation == "LENGTH":
            if len(self.inputs) == 2:
                self.sockets.remove_input(self,self.inputs[1])
            if self.outputs[0].bl_idname == "SN_VectorSocket":
                self.sockets.remove_output(self,self.outputs[0])
                self.sockets.create_output(self,"FLOAT","Output")

    operation: bpy.props.EnumProperty(items=[("ADD", "Add", "Add two vectors"), ("SUBTRACT", "Subtract", "Subtract two vectors"),
                                            ("CROSS_PRODUCT", "Cross Product", "Calculate the cross product between two vectors"),
                                            ("DOT_PRODUCT", "Dot Product", "Calculate the dot product between two vectors"),
                                            ("DISTANCE", "Distance", "Calculate the distance between two vectors"),
                                            ("LENGTH", "Length", "Calculate the length of the vector")],
                                            update=update_operation,name="Operation", description="The operation you want to commence")

    def inititialize(self,context):
        self.sockets.create_input(self,"VECTOR","Value")
        self.sockets.create_input(self,"VECTOR","Value")
        self.sockets.create_output(self,"VECTOR","Output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

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

    def required_imports(self):
        return ["math"]