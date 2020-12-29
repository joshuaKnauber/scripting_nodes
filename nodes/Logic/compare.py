import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_CompareNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CompareNode"
    bl_label = "Compare"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    operation: bpy.props.EnumProperty(items=[("==", "=", "Equal"), ("!=", "≠", "Not equal"), ("<", "<", "Smaller than"), (">", ">", "Bigger than"), ("<=", "≤", "Smaller or equal to"), (">=", "≥", "Bigger or equal to")],name="Operation", description="The operation you want to commence", update=SN_ScriptingBaseNode.update_needs_compile)

    def on_create(self,context):
        self.add_data_input("Data").copy_name=True
        self.add_data_input("Data").copy_name=True
        self.add_boolean_output("Boolean")


    def draw_node(self, context, layout):
        layout.prop(self, "operation", expand=True)


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""{self.inputs[0].value} {self.operation} {self.inputs[1].value}"""
        }