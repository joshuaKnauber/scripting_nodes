from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy

class SNA_Node_BlendDataObjects(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_BlendDataObjects"
    bl_label = "Objects"

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
        self.add_output("ScriptingBlendDataSocket", "All Objects")
        self.add_output("ScriptingBlendDataSocket", "Scene Objects")
        self.add_output("ScriptingBlendDataSocket", "Selected Objects")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingBlendDataSocket", "Active Object")
        self.add_output("ScriptingBlendDataSocket", "Indexed")

    def generate(self):
        self.outputs["All Objects"].code = f"bpy.data.objects"
        self.outputs["Scene Objects"].code = f"bpy.context.scene.objects"
        self.outputs["Selected Objects"].code = f"bpy.context.view_layer.objects.selected"
        self.outputs["Active Object"].code = f"bpy.context.view_layer.objects.active"
        self.outputs["Indexed"].code = f"bpy.data.objects[{self.inputs['Index'].eval()}]"