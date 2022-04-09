import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_NamedIconNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_NamedIconNode"
    bl_label = "Named Icon"
    node_color = "ICON"

    def on_create(self, context):
        self.add_string_output("Icon")
                
                
    def update_selected(self, context):
        for icon in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items:
            if icon.value == self.icon:
                self.icon_name = icon.name
                return
        self.icon_name = "NONE"
        self["icon"] = 0

    icon: bpy.props.IntProperty(name="Value", description="Value of this socket", update=update_selected)
    icon_name: bpy.props.StringProperty(default="NONE" ,update=SN_ScriptingBaseNode._evaluate)


    def evaluate(self, context):
        self.outputs[0].python_value = f"'{self.icon_name}'"

    def draw_node(self, context, layout):
        op = layout.operator("sn.select_icon", text="Choose Icon", icon_value=self.icon)
        op.icon_data_path = f"bpy.data.node_groups['{self.node_tree.name}'].nodes['{self.name}']"