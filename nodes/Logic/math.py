import bpy
import string
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_MathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MathNode"
    bl_label = "Math"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    operation: bpy.props.EnumProperty(items=[(" + ", "Add", "Add two numbers"),
                                             (" - ", "Subtract", "Subtract two numbers"),
                                             (" * ", "Multiply", "Multiply two numbers"),
                                             (" / ", "Divide", "Divide two numbers"),
                                             ("EXPRESSION","Expression","Enter your own expression")],
                                      name="Operation", description="The operation you want to commence")
    
    expression: bpy.props.StringProperty(default="a + b")
    
    def on_dynamic_add(self,socket, connected_socket):
        alphabet = list(string.ascii_lowercase)
        self.inputs[-1].default_text = alphabet[min(len(alphabet)-1,alphabet.index(self.inputs[-1].default_text)+1)]

    def on_create(self,context):
        self.add_float_input("a")
        self.add_float_input("b")
        self.add_dynamic_float_input("c")
        self.add_float_output("Result")

    def draw_node(self, context, layout):
        layout.prop(self, "operation", text="")
        if self.operation == "EXPRESSION":
            layout.prop(self,"expression",text="")

    def code_evaluate(self, context, touched_socket):
        
        if not self.operation == "EXPRESSION":
            return {
                "code": f"""({self.inputs[0].by_type(separator=self.operation)})"""
            }
            
        else:
            
            expression = self.expression
            for inp in self.inputs:
                expression = expression.replace(inp.default_text, inp.code())
            
            return {
                "code": f"eval(\"{expression}\")"
            }