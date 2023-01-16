import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_VectorMathNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_VectorMathNode"
    bl_label = "Vector Math"
    node_color = "VECTOR"

    def update_operation(self,context):
        if self.operation == "CROSS_PRODUCT":
            self.size = 3

        if self.operation == "LENGTH":
            if len(self.inputs) == 2:
                self.inputs.remove(self.inputs[1])
            self.convert_socket(self.outputs[0], self.socket_names["Float"])
        else:
            if len(self.inputs) == 1:
                self.add_float_vector_input("B").size = self.size
            self.convert_socket(self.outputs[0], self.socket_names["Float Vector"])

        if self.operation in ["DIVIDE"]:
            self.convert_socket(self.inputs[1], self.socket_names["Float"])
        elif len(self.inputs) > 1:
            self.convert_socket(self.inputs[1], self.socket_names["Float Vector"])

        self._evaluate(context)


    def update_size(self,context):
        if self.operation == "CROSS_PRODUCT":
            self["size"] = 3
        self.inputs[0].size = self.size
        self.inputs[1].size = self.size
        self._evaluate(context)

    size: bpy.props.IntProperty(default=3, min=2, max=32,
                                name="Size",
                                description="Size of this the vector",
                                update=update_size)

    operation: bpy.props.EnumProperty(items=[("ADD", "Add", "Add two vectors"),
                                             ("SUBTRACT", "Subtract", "Subtract two vectors"),
                                             ("MULTIPLY", "Multiply", "Multiply two vectors"),
                                             ("DIVIDE", "Divide", "Divide vector by float"),
                                             ("CROSS_PRODUCT", "Cross Product", "Cross Product of two vectors"),
                                             ("DOT_PRODUCT", "Dot Product", "Dot Product of two vectors"),
                                             ("LENGTH", "Length", "Length of a vector")],
                                      name="Operation", description="The operation you want to commence",
                                      update=update_operation)    

    def on_create(self, context):
        self.add_float_vector_input("A")
        self.add_float_vector_input("B")
        self.add_float_vector_output("Vector")

    def evaluate(self, context):
        self.code_import = "import mathutils"
        if self.operation == "ADD":
            self.outputs[0].python_value = f"tuple(mathutils.Vector({self.inputs[0].python_value}) + mathutils.Vector({self.inputs[1].python_value}))"
        elif self.operation == "SUBTRACT":
            self.outputs[0].python_value = f"tuple(mathutils.Vector({self.inputs[0].python_value}) - mathutils.Vector({self.inputs[1].python_value}))"
        elif self.operation == "MULTIPLY":
            self.outputs[0].python_value = f"tuple(mathutils.Vector({self.inputs[0].python_value}) * mathutils.Vector({self.inputs[1].python_value}))"
        elif self.operation == "DIVIDE":
            self.outputs[0].python_value = f"tuple(mathutils.Vector({self.inputs[0].python_value}) / {self.inputs[1].python_value})"
        elif self.operation == "CROSS_PRODUCT":
            self.outputs[0].python_value = f"tuple(mathutils.Vector({self.inputs[0].python_value}).cross(mathutils.Vector({self.inputs[1].python_value})))"
        elif self.operation == "DOT_PRODUCT":
            self.outputs[0].python_value = f"mathutils.Vector({self.inputs[0].python_value}).dot(mathutils.Vector({self.inputs[1].python_value}))"
        elif self.operation == "LENGTH":
            self.outputs[0].python_value = f"mathutils.Vector({self.inputs[0].python_value}).length"


    def draw_node(self, context, layout):
        layout.prop(self, "operation", text="")
        if self.operation != "CROSS_PRODUCT":
            layout.prop(self,"size")