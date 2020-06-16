import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_SceneData(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SceneData"
    bl_label = "Scene Data"
    bl_icon = node_icons["SCENE"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def get_data_type(self, context):
        items = []
        for d_type in bpy.data.rna_type.properties:
            if d_type.type == "COLLECTION":
                items.append((d_type.identifier,d_type.name,d_type.description))
        return sorted(items)

    data_type: bpy.props.EnumProperty(items=get_data_type, name="Data", description="The scene data type", update=socket_update)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["SCENE"]
        self.outputs.new("SN_SceneDataSocket", "Scene Data").display_shape = "SQUARE"

    def draw_buttons(self, context, layout):
        layout.label(text="Data type:")
        layout.prop(self,"data_type", text="")

    def evaluate(self, output):
        return {
            "blocks": [
                {
                    "lines": [
                        ["bpy.data." + self.data_type]
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }

    def data_type(self):
        return eval("bpy.data." + self.data_type)

    def needed_imports(self):
        return []