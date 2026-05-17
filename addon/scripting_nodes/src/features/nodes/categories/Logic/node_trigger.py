from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_Trigger(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Trigger"
    bl_label = "Trigger"
    sn_options = {"ROOT_NODE"}

    @property
    def operator_idname(self):
        namespace = bpy.context.scene.sna.addon.idname_namespace
        return f"{namespace}.trigger_{self.id.lower()}"

    @property
    def operator_class_name(self):
        class_prefix = bpy.context.scene.sna.addon.class_prefix
        return f"{class_prefix}_OT_Trigger_{self.id}"

    def draw(self, context, layout):
        row = layout.row()
        row.scale_y = 1.5
        try:
            row.operator(self.operator_idname, text="Trigger")
        except (RuntimeError, AttributeError):
            row.label(text="Trigger (addon not loaded)", icon="ERROR")

    def on_create(self):
        self.add_output("ScriptingLogicSocket")

    def generate(self):
        body = self.outputs[0].eval("pass")
        self.code_module = f"""
class {self.operator_class_name}(bpy.types.Operator):
    bl_idname = "{self.operator_idname}"
    bl_label = "Trigger"
    bl_options = {{"REGISTER", "UNDO"}}

    def execute(self, context):
        {indent(body, 2)}
        return {{"FINISHED"}}
"""
