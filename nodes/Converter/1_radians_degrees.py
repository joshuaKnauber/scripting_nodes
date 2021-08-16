import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RadiansNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RadiansNode"
    bl_label = "Convert Radians/Degrees"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    operation: bpy.props.EnumProperty(items=[("degrees", "Radians to Degrees", "Convert Radians to Degrees"), ("radians", "Degrees to Radians", "Convert Degrees to radians")],name="Operation", update=SN_ScriptingBaseNode.auto_compile)


    def on_create(self,context):
        self.add_float_input("Input")
        self.add_float_output("Output")


    def draw_node(self, context, layout):
        col = layout.column()
        col.prop(self, "operation", text="")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""math.{self.operation}({self.inputs[0].code()})"""
        }