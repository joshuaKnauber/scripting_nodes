import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_NodeGroupInputNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NodeGroupInputNode"
    bl_label = "Group Input"
    bl_width_min = 200

    def update_execute_type(self, context):
        pass

    execute_type: bpy.props.EnumProperty(
        items=[
            ("EXECUTE", "Execute", "For execute functions"),
            ("INTERFACE", "Interface", "For interface functions"),
        ],
        name="Type",
        default="EXECUTE",
        update=update_execute_type,
    )

    def on_create(self, context):
        self.add_execute_output()
        self.add_dynamic_data_output("Data")

    def draw_node(self, context, layout):
        layout.prop(self, "execute_type", expand=True)
