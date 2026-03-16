from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_OnRenderFinish(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_OnRenderFinish"
    bl_label = "On Render Finish"
    sn_options = {"ROOT_NODE"}

    action: bpy.props.EnumProperty(
        items=[
            ("render_cancel", "Cancel", "On canceling a render job"),
            ("render_post", "After", "On render (after)"),
            ("render_complete", "Complete", "On completion of render job"),
        ],
        name="Time of Action",
        description="When the event handler should run",
        update=lambda self, ctx: self._generate(),
    )

    def on_create(self):
        self.add_output("ScriptingLogicSocket")

    def draw(self, context, layout):
        layout.prop(self, "action", expand=True)

    @property
    def handler_name(self):
        return f"{self.action}_handler_{self.id}"

    def generate(self):
        output_code = self.outputs[0].eval()

        self.code_global = "from bpy.app.handlers import persistent"

        self.code = f"""
@persistent
def {self.handler_name}(dummy):
    {indent(output_code, 1) if output_code.strip() else 'pass'}
"""

        self.code_register = f"bpy.app.handlers.{self.action}.append({self.handler_name})"
        self.code_unregister = f"bpy.app.handlers.{self.action}.remove({self.handler_name})"
