import re
import bpy
import string
from ...base_node import SN_ScriptingBaseNode



class SN_MathNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_MathNode"
    bl_label = "Math"
    node_color = "FLOAT"

    def _migrate_data(self, socket, new_name):
        """Helper to migrate data keys when renaming sockets"""
        if socket.name == new_name:
            return

        # Helpers to construct keys
        is_output_str = "out" if socket.is_output else "in"
        idx = socket.index
        old_prefix = f"_socket_{is_output_str}_{idx}_{socket.name}"
        new_prefix = f"_socket_{is_output_str}_{idx}_{new_name}"

        # Find all keys belonging to this socket (including subtypes)
        keys_to_migrate = []
        for key in self.keys():
            if key.startswith(old_prefix):
                keys_to_migrate.append(key)
        
        # Move data
        for old_key in keys_to_migrate:
            new_key = old_key.replace(old_prefix, new_prefix, 1)
            self[new_key] = self[old_key]
            del self[old_key]

        socket.set_name_silent(new_name)

    def on_dynamic_socket_add(self, socket):
        super().on_dynamic_socket_add(socket)
        alphabet = list(string.ascii_lowercase)
        if len(self.inputs) > 26:
            self.inputs.remove(socket)
        for x, socket in enumerate(self.inputs):
            target_name = alphabet[x]
            self._migrate_data(socket, target_name)

    def on_dynamic_socket_remove(self, index, is_output):
        super().on_dynamic_socket_remove(index, is_output)
        alphabet = list(string.ascii_lowercase)
        if self.inputs[-2].name != "z" and self.inputs[-1].hide:
            self.inputs[-1].set_hide(False)
        if self.inputs[-2].name != "z":
            # Just re-run the full rename loop to stick to consistent state
            for x, socket in enumerate(self.inputs):
                 # Skip the last one if it's hidden/dynamic placeholder logic (handled by Math logic usually)
                 # But sticking to the pattern:
                 if x < 26: 
                     target_name = alphabet[x]
                     self._migrate_data(socket, target_name)

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
