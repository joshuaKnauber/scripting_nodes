import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_MathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MathNode"
    bl_label = "Math"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    operation: bpy.props.EnumProperty(items=[(" + ", "Add", "Add two numbers"), (" - ", "Subtract", "Subtract two numbers"), (" * ", "Multiply", "Multiply two numbers"), (" / ", "Divide", "Divide two numbers")],name="Operation", description="The operation you want to commence", update=SN_ScriptingBaseNode.auto_compile)

    def on_create(self,context):
        self.add_float_input("Value").copy_name=True
        self.add_float_input("Value").copy_name=True
        self.add_float_output("Result")

    def draw_node(self, context, layout):
        layout.prop(self, "operation", expand=True)

    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""({self.inputs[0].value}{self.operation}{self.inputs[1].value})"""
        }