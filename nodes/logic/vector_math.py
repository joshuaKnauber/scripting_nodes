#SN_VectorMathNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_VectorMathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_VectorMathNode"
    bl_label = "Vector Math"
    bl_icon = "CON_TRANSLIKE"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>do vector math operations</>."
                ""],
        "python": ["mathutils.Vector(<blue>(1,2,3)</>) * mathutils.Vector(<blue>(4,5,6))</>)"]

    }

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
                                            ("MULTIPLY", "Multiply", "Multiply two vectors"), ("DIVIDE", "Divide", "Divide two vectors"),
                                            ("CROSS_PRODUCT", "Cross Product", "Calculate the cross product between two vectors"),
                                            ("DOT_PRODUCT", "Dot Product", "Calculate the dot product between two vectors"),
                                            ("LENGTH", "Length", "Calculate the length of the vector")],
                                            update=update_operation,name="Operation", description="The operation you want to commence")

    def update_four(self,context):
        self.inputs[0].use_four_numbers = self.use_four
        self.inputs[1].use_four_numbers = self.use_four

    use_four: bpy.props.BoolProperty(default=False,name="Use Four Numbers", update=update_four)

    def inititialize(self,context):
        self.sockets.create_input(self,"VECTOR","Value")
        self.sockets.create_input(self,"VECTOR","Value")
        self.sockets.create_output(self,"VECTOR","Output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")
        layout.prop(self,"use_four")

    def evaluate(self, socket, node_data, errors):
        v1 = node_data["input_data"][0]["code"]

        if not self.operation == "LENGTH":
            v2 = node_data["input_data"][1]["code"]

        operation = [v1]

        values = "xyz"
        if self.use_four:
            values = "xyzw"
        
        if self.operation == "ADD":
            operation = ["(mathutils.Vector(",v1,") + mathutils.Vector(",v2,")).",values]
        elif self.operation == "SUBTRACT":
            operation = ["(mathutils.Vector(",v1,") - mathutils.Vector(",v2,")).",values]
        elif self.operation == "MULTIPLY":
            operation = ["mathutils.Vector(x * y for x, y in zip(",v1,", ",v2,")).",values]
        elif self.operation == "DIVIDE":
            operation = ["mathutils.Vector(x / y for x, y in zip(",v1,", ",v2,")).",values]
        elif self.operation == "CROSS_PRODUCT":
            operation = ["(mathutils.Vector(",v1,").cross(mathutils.Vector(",v2,"))).",values]
        elif self.operation == "DOT_PRODUCT":
            operation = ["(mathutils.Vector(",v1,").dot(mathutils.Vector(",v2,")))"]
        elif self.operation == "LENGTH":
            operation = ["mathutils.Vector(",v1,").length"]


        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        operation
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }

    def required_imports(self):
        return ["mathutils"]