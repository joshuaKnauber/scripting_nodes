import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ObjectTypeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectTypeNode"
    bl_label = "Object Type"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    types: bpy.props.EnumProperty(items=[('MESH', 'Mesh', ''), ('CURVE', 'Curve', ''), ('SURFACE', 'Surface', ''), ('META', 'Metaball', ''), ('FONT', 'Text', ''), ('HAIR', 'Hair', ''), ('POINTCLOUD', 'Point Cloud', ''), ('VOLUME', 'Volume', ''), ('GPENCIL', 'Grease Pencil', ''), ('ARMATURE', 'Armature', ''), ('LATTICE', 'Lattice', ''), ('EMPTY', 'Empty', ''), ('LIGHT', 'Light', ''), ('LIGHT_PROBE', 'Light Probe', ''), ('CAMERA', 'Camera', ''), ('SPEAKER', 'Speaker', '')],
                                    update=SN_ScriptingBaseNode.auto_compile,
                                    name="Type",
                                    description="The type which the object is compared to")

    def on_create(self,context):
        self.add_blend_data_input("Object")
        self.add_boolean_output("Is Type")

    def draw_node(self,context,layout):
        layout.prop(self, "types", text="")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"{self.inputs[0].code()}.type==\"{self.types}\""
        }