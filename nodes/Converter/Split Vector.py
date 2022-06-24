import bpy
import string
from ..base_node import SN_ScriptingBaseNode



class SN_SplitVectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SplitVectorNode"
    bl_label = "Split Vector"
    node_color = "VECTOR"

    def update_vector_type(self,context):
        self.convert_socket(self.inputs[0], self.socket_names[self.vector_type])
        for output in self.outputs:
            self.convert_socket(output, self.socket_names[self.vector_type[:-7]])
        self._evaluate(context)

    def update_size(self,context):
        self.inputs[0].size = self.size
        if len(self.outputs) > self.size:
            for i in range(len(self.outputs)-self.size):
                self.outputs.remove(self.outputs[-1])
        elif self.size > len(self.outputs):
            for i in range(self.size-len(self.outputs)):
                alphabet = list(string.ascii_lowercase) + list(string.ascii_uppercase)
                if self.vector_type == "Float Vector":
                    self.add_float_output(alphabet[len(self.outputs)])
                elif self.vector_type == "Integer Vector":
                    self.add_integer_output(alphabet[len(self.outputs)])
                elif self.vector_type == "Boolean Vector":
                    self.add_boolean_output(alphabet[len(self.outputs)])
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
        self.add_float_vector_input("Vector")
        self.add_float_output("a")
        self.add_float_output("b")
        self.add_float_output("c")


    def evaluate(self, context):
        if self.vector_type == "Integer Vector":
            for i in range(len(self.outputs)):
                self.outputs[i].python_value = f"int({self.inputs[0].python_value}[{i}])"
        else:
            for i in range(len(self.outputs)):
                self.outputs[i].python_value = f"{self.inputs[0].python_value}[{i}]"

    def draw_node(self, context, layout):
        layout.prop(self, "vector_type")
        layout.prop(self, "size")