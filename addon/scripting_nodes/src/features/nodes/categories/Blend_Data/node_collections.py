from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy

class SNA_Node_BlendDataCollections(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_BlendDataCollections"
    bl_label = "Collections"

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
        self.add_output("ScriptingBlendDataSocket", "All Collections")
        self.add_output("ScriptingBlendDataSocket", "Scene Collections")
        self.add_output("ScriptingBlendDataSocket", "Scene Collection")
        self.add_output("ScriptingBlendDataSocket", "Active Collection")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingBlendDataSocket", "Indexed")

    def generate(self):
        self.outputs["All Collections"].code = f"bpy.data.collections"
        self.outputs["Scene Collections"].code = f"bpy.context.scene.collection.children"
        self.outputs["Scene Collection"].code = f"bpy.context.scene.collection"
        self.outputs["Active Collection"].code = f"bpy.context.collection"
        self.outputs["Indexed"].code = f"bpy.data.collections[{self.inputs['Index'].eval()}]"