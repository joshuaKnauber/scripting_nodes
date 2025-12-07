import bpy
import os
from ..base_node import SN_ScriptingBaseNode


class SN_AssetNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_AssetNode"
    bl_label = "Asset"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_output("Path").subtype = "FILE_PATH"

    asset: bpy.props.StringProperty(
        name="Asset",
        description="Asset to get the path from",
        update=SN_ScriptingBaseNode._evaluate,
    )

    def evaluate(self, context):
        if self.asset and self.asset in context.scene.sn.assets:
            if context.scene.sn.assets[self.asset].path:
                self.outputs["Path"].python_value = (
                    f"r'{context.scene.sn.assets[self.asset].path}'"
                )
                return
        self.outputs["Path"].python_value = "''"

    def evaluate_export(self, context):
        if self.asset and self.asset in context.scene.sn.assets:
            if context.scene.sn.assets[self.asset].path:
                self.code_import = "import os"
                name = os.path.basename(context.scene.sn.assets[self.asset].path)
                if not name:
                    name = os.path.basename(
                        os.path.dirname(context.scene.sn.assets[self.asset].path)
                    )
                self.outputs["Path"].python_value = (
                    f"os.path.join(os.path.dirname(__file__), 'assets', '{name}')"
                )
                return
        self.outputs["Path"].python_value = "''"

    def draw_node(self, context, layout):
        layout.prop_search(
            self, "asset", context.scene.sn, "assets", item_search_property="name"
        )
