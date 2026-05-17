from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_OnFrameChange(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_OnFrameChange"
    bl_label = "On Frame Change"
    sn_options = {"ROOT_NODE"}

    action: bpy.props.EnumProperty(
        items=[
            (
                "frame_change_pre",
                "Before",
                "Called after frame change for playback and rendering, before any data is evaluated for the new frame",
            ),
            (
                "frame_change_post",
                "After",
                "Called after frame change for playback and rendering, after the data has been evaluated for the new frame",
            ),
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

        self.code_imports = "from bpy.app.handlers import persistent"

        self.code_module = f"""
@persistent
def {self.handler_name}(dummy):
    {indent(output_code, 1) if output_code.strip() else 'pass'}
"""

        self.code_register = f"bpy.app.handlers.{self.action}.append({self.handler_name})"
        self.code_unregister = f"bpy.app.handlers.{self.action}.remove({self.handler_name})"
