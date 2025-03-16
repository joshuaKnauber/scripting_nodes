from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy

class BlendDataBaseNode(ScriptingBaseNode):

    data_type = ""
    data_type_plural = ""
    
    active_path = ""
    data_path = ""

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
        self.add_output("ScriptingBlendDataSocket", f"All {self.data_type_plural}")
        if self.active_path: self.add_output("ScriptingBlendDataSocket",f"Active {self.data_type}")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingBlendDataSocket", "Indexed")

    def generate(self):
        self.outputs[f"All {self.data_type_plural}"].code = self.data_path
        if self.active_path: self.outputs[f"Active {self.data_type}"].code = self.active_path
        self.outputs["Indexed"].code = f"{self.data_path}[{self.inputs['Index'].eval()}]"