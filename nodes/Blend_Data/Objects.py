import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ObjectBlendDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectBlendDataNode"
    bl_label = "Object"
    node_color = "PROPERTY"
    
    def on_create(self, context):
        self.add_collection_property_output("All Objects")
        self.add_collection_property_output("Active Scene Objects")
        self.add_list_output("Selected Objects")
        self.add_property_output("Active Object")
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
        self.outputs["All Objects"].python_value = f"bpy.data.objects"
        self.outputs["Active Scene Objects"].python_value = f"bpy.context.scene.objects"
        self.outputs["Selected Objects"].python_value = f"bpy.context.selected_objects"
        self.outputs["Active Object"].python_value = f"bpy.context.active_object"
        self.outputs["Indexed"].python_value = f"bpy.data.objects[{self.inputs[0].python_value}]"

    def draw_node(self, context, layout):
        layout.prop(self, "index_type", expand=True)