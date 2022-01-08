import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_PropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PropertyNode"
    bl_label = "Display Property"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_icon_input("Icon")
        
    prop_type: bpy.props.EnumProperty(name="Prop Type",
                                    description="Use a custom panel as a parent",
                                    items=[("BLENDER", "Blender", "Blender", "BLENDER", 0),
                                           ("CUSTOM", "Custom", "Custom", "FILE_SCRIPT", 1)],
                                    update=SN_ScriptingBaseNode._evaluate)
    
    prop_name: bpy.props.StringProperty(name="Property",
                                    description="The property to display",
                                    update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        if self.prop_name and self.prop_name in context.scene.sn.properties:
            prop = context.scene.sn.properties[self.prop_name]
            self.code = f"{self.active_layout}.prop(context.scene, '{prop.python_name}' ,text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value})"
        else:
            self.code = ""

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop_search(self, "prop_name", context.scene.sn, "properties", text="")
        row.prop(self, "prop_type", text="", icon_only=True)