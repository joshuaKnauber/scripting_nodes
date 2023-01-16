import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_CollectionsBlendDataNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_CollectionsBlendDataNode"
    bl_label = "Collections"
    node_color = "PROPERTY"
    
    def on_create(self, context):
        self.add_collection_property_output("All Collections")
        self.add_collection_property_output("Scene Collections")
        self.add_property_output("Scene Collection")
        self.add_property_output("Active Collection")
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
        self.outputs["All Collections"].python_value = f"bpy.data.collections"
        self.outputs["Scene Collections"].python_value = f"bpy.context.scene.collection.children"
        self.outputs["Scene Collection"].python_value = f"bpy.context.scene.collection"
        self.outputs["Active Collection"].python_value = f"bpy.context.collection"
        self.outputs["Indexed"].python_value = f"bpy.data.collections[{self.inputs[0].python_value}]"

    def draw_node(self, context, layout):
        layout.prop(self, "index_type", expand=True)