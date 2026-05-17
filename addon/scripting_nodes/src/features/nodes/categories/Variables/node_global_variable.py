from ....sockets.socket_types import DATA_SOCKET_ENUM_ITEMS
from .....lib.utils.sockets.modify import update_socket_type
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_GlobalVariable(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GlobalVariable"
    bl_label = "Global Variable"
    sn_options = {"ROOT_NODE"}

    def update_data_type(self, context):
        update_socket_type(self.inputs[0], self.data_type)
        self._generate()

    data_type: bpy.props.EnumProperty(
        items=DATA_SOCKET_ENUM_ITEMS, name="Data Type", update=update_data_type
    )

    def on_create(self):
        self.add_input("ScriptingDataSocket", "Initial Value")

    def draw(self, context, layout):
        layout.prop(self, "data_type", text="")

    def generate(self):
        self.code_module = f"""
            _var_{self.id} = {self.inputs[0].eval()}

            def get_var_{self.id}():
                return _var_{self.id}

            def set_var_{self.id}(value):
                global _var_{self.id}
                _var_{self.id} = value
        """
