import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_MeshBlendDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MeshBlendDataNode"
    bl_label = "Meshes"
    node_color = "PROPERTY"
    
    def on_create(self, context):
        self.add_collection_property_output("All Meshes")
        self.add_list_output("Active Scene Meshes")
        self.add_property_output("Active Object Mesh")
        self.add_property_output("Indexed")
        self.add_integer_input("Index")

    def update_index_type(self, context):
        inp = self.convert_socket(self.inputs[0], self.socket_names[self.index_type])
        inp.name = "Index" if self.index_type == "Integer" else "Name"
        self._evaluate(context)
        
    index_type: bpy.props.EnumProperty(name="Index Type",
                                description="The type of index to use",
                                items=[("Integer", "Index", "Starts at 0. Negative indices go to the back of the list."),
                                       ("String", "Name", "Refers to the name property of the element.")],
                                update=update_index_type)
        
    def evaluate(self, context):
        self.outputs["All Meshes"].python_value = f"bpy.data.meshes"
        self.outputs["Active Scene Meshes"].python_value = f"list(filter(lambda obj: obj, [obj.data if obj.type == 'MESH' else None for obj in bpy.context.scene.objects]))"
        self.outputs["Active Object Mesh"].python_value = f"(bpy.context.active_object.data if bpy.context.active_object.type == 'MESH' else None)"
        self.outputs["Indexed"].python_value = f"bpy.data.meshes[{self.inputs[0].python_value}]"

    def draw_node(self, context, layout):
        layout.prop(self, "index_type", expand=True)