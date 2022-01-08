import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IconViewNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IconViewNode"
    bl_label = "Icon View"
    node_color = "INTERFACE"
    bl_width_default = 200
    # TODO
    def on_create(self, context):
        self.add_interface_input()
        self.add_boolean_input("Show Labels")
        self.add_float_input("Scale").default_value = 5
        self.add_float_input("Scale Popup").default_value = 5
            
    prop_name: bpy.props.StringProperty(name="Property",
                                    description="The property to display",
                                    update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        if self.prop_name and self.prop_name in context.scene.sn.properties:
            prop = context.scene.sn.properties[self.prop_name]
            self.code = f"{self.active_layout}.template_icon_view(context.scene, '{prop.python_name}', show_labels={self.inputs['Show Labels'].python_value}, scale={self.inputs['Scale'].python_value}, scale_popup={self.inputs['Scale Popup'].python_value})"
        else:
            self.code = ""

    def draw_node(self, context, layout):
        layout.prop_search(self, "prop_name", context.scene.sn, "properties", text="")
