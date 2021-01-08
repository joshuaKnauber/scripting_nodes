import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_BoolVectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BoolVectorNode"
    bl_label = "Boolean Vector"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    value: bpy.props.BoolVectorProperty(name="Vector Value",
                                         size=3)

    value_four: bpy.props.BoolVectorProperty(name="Vector Value",
                                         size=4)
    
    def update_size(self,context):
        if self.use_four:
            self.outputs[0].subtype = "VECTOR4"
        else:
            self.outputs[0].subtype = "VECTOR3"

    use_four: bpy.props.BoolProperty(default=False,
                                     name="Vector 4",
                                     update=update_size)

    def on_create(self,context):
        out = self.add_boolean_output("Vector")
        out.mirror_name = True
        out.subtype = "VECTOR3"
        

    def draw_node(self,context,layout):
        layout.prop(self, "use_four")

        col = layout.column(align = True)
        if self.use_four:
            for i in range(4):
                col.prop(self, "value_four", toggle=True, text=str(self.value_four[i]), index=i)
        else:
            for i in range(3):
                col.prop(self, "value", toggle=True, text=str(self.value[i]), index=i)


    def code_evaluate(self, context, touched_socket):

        value = str((self.value[0],self.value[1],self.value[2]))
        if self.use_four:
            value = str((self.value_four[0],self.value_four[1],self.value_four[2],self.value_four[3]))

        return {
            "code": f"{value}"
        }