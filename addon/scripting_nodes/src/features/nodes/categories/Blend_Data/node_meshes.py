from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy

class SNA_Node_BlendDataMeshes(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_BlendDataMeshes"
    bl_label = "Meshes"

    def update_index_type(self, context):
        if self.index_type == "String":
            update_socket_type(self.inputs['Index'], "ScriptingStringSocket")
        elif self.index_type == "Integer":
            update_socket_type(self.inputs['Index'], "ScriptingIntegerSocket")
        self._generate()

    index_type: bpy.props.EnumProperty(name="Index Type",
                                description="The type of index to use",
                                items=[("Integer", "Index", "Starts at 0. Negative indices go to the back of the list."),
                                       ("String", "Name", "Refers to the name property of the element.")],
                                update=update_index_type)

    def draw(self, context, layout):
        layout.prop(self, "index_type", text="text", expand=True)

    def on_create(self):
        self.add_output("ScriptingBlendDataSocket", "All Meshes")
        self.add_output("ScriptingBlendDataSocket", "Scene Meshes")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingBlendDataSocket", "Active Object Mesh")
        self.add_output("ScriptingBlendDataSocket", "Indexed")

    def generate(self):
        self.outputs["All Meshes"].code = f"bpy.data.meshes"
        self.outputs["Scene Meshes"].code = f"list(filter(lambda obj: obj, [obj.data if obj.type == 'MESH' else None for obj in bpy.context.scene.objects]))"
        self.outputs["Active Object Mesh"].code = f"(bpy.context.active_object.data if bpy.context.active_object.type == 'MESH' else None)"
        self.outputs["Indexed"].code = f"bpy.data.meshes[{self.inputs['Index'].eval()}]"