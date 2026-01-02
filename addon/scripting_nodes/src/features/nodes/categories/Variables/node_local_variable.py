from .....lib.utils.sockets.modify import update_socket_type
from ....sockets.socket_types import DATA_SOCKET_ENUM_ITEMS
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_LocalVariable(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_LocalVariable"
    bl_label = "Local Variable"

    def update_data_type(self, context):
        update_socket_type(self.inputs[1], self.data_type)
        update_socket_type(self.outputs[1], self.data_type)
        self._generate()

    data_type: bpy.props.EnumProperty(
        items=DATA_SOCKET_ENUM_ITEMS, name="Data Type", update=update_data_type
    )

    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingDataSocket", "Initial Value")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingDataSocket", "Value")

    def draw(self, context, layout):
        layout.prop(self, "data_type", text="")

    def generate(self):
        self.code = f"""
            var_{self.id} = {self.inputs[1].eval()}
            {indent(self.outputs[0].eval(), 3)}
        """
        self.outputs[1].code = f"var_{self.id}"
