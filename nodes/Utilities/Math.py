from cmath import exp
import bpy
import string
from ..base_node import SN_ScriptingBaseNode



class SN_MathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MathNode"
    bl_label = "Math"
    node_color = "FLOAT"

    def on_dynamic_socket_add(self, socket):
        alphabet = list(string.ascii_lowercase)
        if self.inputs[-1].name == "z":
            self.inputs[-1].set_hide(True)
        else:
            self.inputs[-1].name = alphabet[alphabet.index(self.inputs[-2].name)+1]

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

    def replace_in_expression(self,expression, varname, value):
        parts = expression.split(varname)

        for char in string.ascii_lowercase:
            if not char == varname:
                expression = expression.replace(f"{varname}{char}", f"#{char}")
                expression = expression.replace(f"{char}{varname}", f"{char}#")

        expression = expression.replace(varname,value)
        expression = expression.replace("#",varname)

        return expression

    def evaluate(self, context):
        if not self.operation == "EXPRESSION":
            values = [inp.python_value for inp in self.inputs[:-1]]
            self.outputs[0].python_value = f"{self.operation.join(values)}"
            self.outputs[1].python_value = f"int({self.operation.join(values)})"

        else:
            expression = self.expression
            for inp in self.inputs:
                expression = self.replace_in_expression(expression, inp.name, inp.python_value)
            self.outputs[0].python_value = f"eval(\"{expression}\")"
            self.outputs[1].python_value = f"int(eval(\"{expression}\"))"
