import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_DefineDataType(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DefineDataType"
    bl_label = "Define Data Type"
    node_color = "DEFAULT"

    def get_data_items(self,context):
        items = []
        for label in list(self.socket_names.keys())[3:]:
            items.append((self.socket_names[label], label, self.socket_names[label]))
        return items

    def update_conversion(self, context):
        self.convert_socket(self.outputs[0], self.convert_to)

    convert_to: bpy.props.EnumProperty(items=get_data_items,
                                    update=update_conversion,
                                    name="Data",
                                    description="The type of data that you want to set the data input to",)

    def draw_node(self, context, layout):
        layout.prop(self, "convert_to", text="")

    def on_create(self, context):
        self.add_data_input("Data")
        self.add_string_output("Data")

    def evaluate(self, context):
        self.outputs[0].python_value = self.inputs[0].python_value
