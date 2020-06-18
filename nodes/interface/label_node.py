import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from random import randint


class SN_Label(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_Label"
    bl_label = "Label"
    bl_icon = node_icons["INTERFACE"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def init(self, context):
        self.panel_uid = str(randint(1111,9999))

        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new("SN_StringSocket", "Text").value = "New Label"

        self.outputs.new("SN_LayoutSocket", "Layout")

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self, output):
        error_list = []

        layout_type, errors = self.SocketHandler.socket_value(self.outputs[0])
        error_list += errors

        text_input, errors = self.SocketHandler.socket_value(self.inputs[0])
        error_list += errors

        return {
            "blocks": [
                {
                    "lines": [
                        [layout_type,".label(text=\"",text_input,"\")"]
                    ],
                    "indented": []
                }
            ],
            "errors": error_list
        }

    def layout_type(self):
        return "layout"

    def needed_imports(self):
        return ["bpy"]

    def get_register_block(self):
        idname, _ = self._get_panel_name()
        return ["bpy.utils.register_class("+idname+")"]

    def get_unregister_block(self):
        idname, _ = self._get_panel_name()
        return ["bpy.utils.unregister_class("+idname+")"]