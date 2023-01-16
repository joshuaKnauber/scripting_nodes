import re
import bpy
import string
from ...base_node import SN_ScriptingBaseNode



class SN_MathNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_MathNode"
    bl_label = "Math"
    node_color = "FLOAT"

    def on_dynamic_socket_add(self, socket):
        alphabet = list(string.ascii_lowercase)
        if len(self.inputs) > 26:
            self.inputs.remove(socket)
        for x, socket in enumerate(self.inputs):
            socket.name = alphabet[x]

    def on_dynamic_socket_remove(self, index, is_output):
        alphabet = list(string.ascii_lowercase)
        if self.inputs[-2].name != "z" and self.inputs[-1].hide:
            self.inputs[-1].set_hide(False)
        if self.inputs[-2].name != "z":
            self.inputs[-1].name = alphabet[alphabet.index(self.inputs[-2].name)+1]

    operation: bpy.props.EnumProperty(items=[(" + ", "Add", "Add two numbers"),
                                             (" - ", "Subtract", "Subtract two numbers"),
                                             (" * ", "Multiply", "Multiply two numbers"),
                                             (" / ", "Divide", "Divide two numbers"),
                                             ("EXPRESSION","Expression","Enter your own expression")],
                                      name="Operation", 
                                      description="Operation to perform on the input data",
                                      update=SN_ScriptingBaseNode._evaluate)

    expression: bpy.props.StringProperty(default="a + b", update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_float_input("a")
        self.add_float_input("b")
        self.add_dynamic_float_input("c")
        self.add_float_output("Float Result")
        self.add_integer_output("Integer Result")

    def draw_node(self, context, layout):
        layout.prop(self, "operation", text="")
        if self.operation == "EXPRESSION":
            layout.prop(self,"expression",text="")
            
    def multiple_replace(self, string, rep_dict):
        for key, value in rep_dict.items():
            string = re.sub(rf'\b{key}\b', value, string)
        return string

    def evaluate(self, context):
        if not self.operation == "EXPRESSION":
            values = [inp.python_value for inp in self.inputs[:-1]]
            self.outputs[0].python_value = f"float({self.operation.join(values)})"
            self.outputs[1].python_value = f"int({self.operation.join(values)})"

        else:
            self.code_import = "import math"
            expression = self.expression
            
            to_replace = {}
            for inp in self.inputs:
                if not inp.dynamic:
                    to_replace[inp.name] = inp.python_value

            expression = self.multiple_replace(expression, to_replace)

            self.outputs[0].python_value = f"eval(\"{expression}\")"
            self.outputs[1].python_value = f"int(eval(\"{expression}\"))"
