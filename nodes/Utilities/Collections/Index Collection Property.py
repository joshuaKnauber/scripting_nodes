import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_IndexCollectionPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IndexCollectionPropertyNode"
    bl_label = "Index Collection Property"
    node_color = "PROPERTY"
    
    def on_create(self, context):
        self.add_collection_property_input()
        self.add_integer_input("Index")
        self.add_property_output()

    def update_index_type(self, context):
        inp = self.convert_socket(self.inputs[1], self.socket_names[self.index_type])
        inp.name = "Index" if self.index_type == "Integer" else "Name"
        self._evaluate(context)
        
    index_type: bpy.props.EnumProperty(name="Index Type",
                                description="The type of index to use",
                                items=[("Integer", "Index", "Starts at 0. Negative indices go to the back of the list."),
                                       ("String", "Name", "Refers to the name property of the element.")],
                                update=update_index_type)
        
    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs[0].python_value}[{self.inputs[1].python_value}]"

    def draw_node(self, context, layout):
        layout.prop(self, "index_type", expand=True)