import bpy
from ...compile.compiler import compiler
from ...handler.error_handling import ErrorHandler
from ...handler.get_socket_value import SocketHandler
from ...handler.ui_location_handler import UiLocationHandler
from ...handler.operator_handler import OperatorHandler

class SN_ScriptingBaseNode:
    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000

    _should_be_registered = False

    _dynamic_layout_sockets = False

    _debug_node = False

    ErrorHandler = ErrorHandler()
    SocketHandler = SocketHandler()
    UiLocationHandler = UiLocationHandler()
    OperatorHandler = OperatorHandler()

    icon: bpy.props.StringProperty(default="")

    def socket_update(self, context):
        compiler().socket_update()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'

    def _update_layout_sockets(self):
        for input_socket in self.inputs:
            if input_socket.bl_idname == "SN_LayoutSocket":
                if not input_socket.is_linked:
                    self.inputs.remove(input_socket)
        self.inputs.new("SN_LayoutSocket","Layout")

    def update(self):
        compiler().socket_update()
        if self._dynamic_layout_sockets:
            self._update_layout_sockets()

    def draw_icon_chooser(self,layout):
        """ draws the options for choosing an icon """
        box = layout.box()
        row = box.row()
        row.operator("scripting_nodes.choose_icon",text="Icons" , icon="PRESET").node_name = self.name
        if self.icon:
            row.label(icon=self.icon,text="")
            row.operator("scripting_nodes.clear_icon",text="",icon="PANEL_CLOSE",emboss=False).node_name = self.name
    
    def evaluate(self, output):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines

                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines

                    ]
                }
            ],
            "errors": [
                {
                    "error": "",
                    "node": self,
                    "socket": None
                }
            ]
        }

    def layout_type(self):
        return ""

    def data_type(self, output):
        return None

    def get_register_block(self):
        return ["pass"]

    def get_unregister_block(self):
        return ["pass"]

    def needed_imports(self):
        return ["bpy"]