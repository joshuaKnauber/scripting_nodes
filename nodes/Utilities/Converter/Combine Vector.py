import bpy
import string
from ...base_node import SN_ScriptingBaseNode



class SN_CombineVectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CombineVectorNode"
    bl_label = "Combine Vector"
    node_color = "VECTOR"

    def update_vector_type(self,context):
        self.convert_socket(self.outputs[0], self.socket_names[self.vector_type])
        for input in self.inputs:
            self.convert_socket(input, self.socket_names[self.vector_type[:-7]])
        self._evaluate(context)

    def update_size(self,context):
        self.outputs[0].size = self.size
        if len(self.inputs) > self.size:
            for i in range(len(self.inputs)-self.size):
                self.inputs.remove(self.inputs[-1])
        elif self.size > len(self.inputs):
            for i in range(self.size-len(self.inputs)):
                alphabet = list(string.ascii_lowercase) + list(string.ascii_uppercase)
                if self.vector_type == "Float Vector":
                    self.add_float_input(alphabet[len(self.inputs)])
                elif self.vector_type == "Integer Vector":
                    self.add_integer_input(alphabet[len(self.inputs)])
                elif self.vector_type == "Boolean Vector":
                    self.add_boolean_input(alphabet[len(self.inputs)])
        self._evaluate(context)

    vector_type: bpy.props.EnumProperty(name="Type",
                                        description="The type of vector that should be used",
                                        items=[("Float Vector","Float","Float Vector"),
                                               ("Integer Vector","Integer","Integer Vector"),
                                               ("Boolean Vector","Boolean","Boolean Vector")],
                                        update=update_vector_type)

    size: bpy.props.IntProperty(default=3, min=2, max=32,
                                name="Size",
                                description="Size of this the vector",
                                update=update_size)

    def on_create(self, context):
        self.add_float_vector_output("Vector")
        self.add_float_input("a")
        self.add_float_input("b")
        self.add_float_input("c")


    def evaluate(self, context):
        values = [inp.python_value for inp in self.inputs]
        self.outputs[0].python_value = f"({', '.join(values)})"

    def draw_node(self, context, layout):
        layout.prop(self, "vector_type")
        layout.prop(self, "size")