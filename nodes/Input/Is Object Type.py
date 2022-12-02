import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_IsObjectType(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IsObjectType"
    bl_label = "Is Object Type"
    node_color = "PROPERTY"


    types: bpy.props.EnumProperty(items=[('MESH', 'Mesh', ''), ('CURVE', 'Curve', ''), ('SURFACE', 'Surface', ''), ('META', 'Metaball', ''), ('FONT', 'Text', ''), ('HAIR', 'Hair', ''), ('POINTCLOUD', 'Point Cloud', ''), ('VOLUME', 'Volume', ''), ('GPENCIL', 'Grease Pencil', ''), ('ARMATURE', 'Armature', ''), ('LATTICE', 'Lattice', ''), ('EMPTY', 'Empty', ''), ('LIGHT', 'Light', ''), ('LIGHT_PROBE', 'Light Probe', ''), ('CAMERA', 'Camera', ''), ('SPEAKER', 'Speaker', '')],
                                    update=SN_ScriptingBaseNode._evaluate,
                                    name="Type",
                                    description="The type which the object is compared to")


    def draw_node(self, context, layout):
        layout.prop(self, "types", text="")

    def on_create(self, context):
        self.add_property_input("Object")
        self.add_boolean_output("Is Type")

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs[0].python_value}.type == '{self.types}'"
