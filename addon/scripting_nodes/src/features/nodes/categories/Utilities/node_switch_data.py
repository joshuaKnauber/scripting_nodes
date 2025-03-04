from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
from scripting_nodes.src.features.sockets.socket_types import DATA_SOCKET_ENUM_ITEMS
import bpy


class SNA_Node_SwitchData(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_SwitchData"
    bl_label = "Switch Data"

    def update_data_type(self, context):
        if len(self.outputs) > 0:
            update_socket_type(self.outputs[0], self.data_type)
            self._generate()

    data_type: bpy.props.EnumProperty(
        items=DATA_SOCKET_ENUM_ITEMS, name="Data Type", update=update_data_type
    )

    def draw(self, context, layout):
        layout.prop(self, "data_type", text="")

    def on_create(self):
        self.add_input("ScriptingBooleanSocket", "Condition")
        self.add_input("ScriptingDataSocket", "False")
        self.add_input("ScriptingDataSocket", "True")
        self.add_output("ScriptingDataSocket", "Result")

    def generate(self):
        if len(self.outputs) == 0:
            return

        condition = self.inputs["Condition"].eval()
        false_value = self.inputs["False"].eval()
        true_value = self.inputs["True"].eval()

        self.outputs[0].code = f"({true_value} if {condition} else {false_value})"
