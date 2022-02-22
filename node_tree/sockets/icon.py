import bpy
from .base_socket import ScriptingSocket



class SN_IconSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_IconSocket"
    group = "DATA"
    bl_label = "Icon"


    default_python_value = "0"
    default_prop_value = 0

    def get_python_repr(self):
        value = self.default_value
        if self.subtype == "BLENDER_ONLY":
            for icon in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items:
                if icon.value == value:
                    return f"'{icon.name}'"
            return "NONE"
        return f"{value}"


    default_value: bpy.props.IntProperty(name="Value",
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)


    subtypes = ["NONE", "BLENDER_ONLY"]
    subtype_values = {"NONE": "default_value", "BLENDER_ONLY": "default_value"}


    def get_color(self, context, node):
        return (1,0.4,0.2)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
        if (not self.is_linked or self.subtype == "BLENDER_ONLY") and not self.is_output:
            row = layout.row()
            row.scale_x = 1.74
            op = row.operator("sn.select_icon", text="Choose Icon", icon_value=self.default_value)
            op.icon_data_path = f"bpy.data.node_groups['{node.node_tree.name}'].nodes['{node.name}'].inputs[{self.index}]"
            op.prop_name = "default_value"

