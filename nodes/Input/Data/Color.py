import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ColorNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ColorNode"
    bl_label = "Color"
    node_color = "VECTOR"

    def update_size(self, context):
        if self.use_four:
            self.inputs[0].subtype = "COLOR_ALPHA"
            self.outputs[0].subtype = "COLOR_ALPHA"
        else:
            self.inputs[0].subtype = "COLOR"
            self.outputs[0].subtype = "COLOR"

    use_four: bpy.props.BoolProperty(default=False,
                                     name="Use Alpha",
                                     update=update_size)

    def on_create(self, context):
        socket = self.add_float_vector_input("Color")
        socket.set_hide(True)
        socket.subtype = "COLOR"
        self.add_float_vector_output("Color").subtype = "COLOR"

    def evaluate(self, context):
        self.outputs["Color"].python_value = self.inputs["Color"].python_value

    def draw_node(self, context, layout):
        layout.prop(self, "use_four")
        self.inputs["Color"].draw_socket(context, layout, self, "")