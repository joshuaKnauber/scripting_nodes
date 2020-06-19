import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_AppendPanel(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AppendPanel"
    bl_label = "Append Panel"
    bl_width_default = 230
    bl_icon = node_icons["INTERFACE"]

    _should_be_registered = True
    _dynamic_layout_sockets = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    panel_uid: bpy.props.StringProperty(default="")

    panel_name: bpy.props.StringProperty(default="")

    def init(self, context):
        self.panel_uid = str(randint(1111,9999))

        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self, output):
        error_list = []
        
        layouts, errors = self.SocketHandler.get_layout_values(self)
        error_list += errors

        return {
            "blocks": [
                {
                    "lines": [
                        ["def append_panel_"+self.panel_uid+"(self, context):"]
                    ],
                    "indented": [
                        ["layout = self.layout"],
                        layouts
                    ]
                }
            ],
            "errors": error_list
        }

    def layout_type(self):
        return "layout"

    def needed_imports(self):
        return ["bpy"]

    def get_register_block(self):
        return ["bpy.types.RENDER_PT_render.append("+"append_panel_"+self.panel_uid+")"]

    def get_unregister_block(self):
        return ["bpy.types.RENDER_PT_render.remove("+"append_panel_"+self.panel_uid+")"]