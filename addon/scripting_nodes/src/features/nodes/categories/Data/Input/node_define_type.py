from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy


class SNA_Node_DefineType(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_DefineType"
    bl_label = "Define Type"
    
    #enum to define the output type
    output_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("STRING", "String", "String"),
            ("INT", "Int", "Int"),
            ("FLOAT", "Float", "Float"),
        ],
        default="STRING",
        update=lambda self, context: self.update_output_socket_type()
    )
    
    def update_output_socket_type(self):
        if self.output_type == "STRING":
            update_socket_type(self.outputs[0], "ScriptingStringSocket")
        elif self.output_type == "INT":
            update_socket_type(self.outputs[0], "ScriptingIntegerSocket")
        elif self.output_type == "FLOAT":
            update_socket_type(self.outputs[0], "ScriptingFloatSocket")

        self._generate()

    def on_create(self):
        #start with converting types to strings
        self.add_input("ScriptingDataSocket", "Data")       
        self.add_output("ScriptingDataSocket", "Data")
        self.update_output_socket_type()
        
    #display the output type
    def draw(self, context, layout):
        layout.prop(self, "output_type", text="")
        
    def generate(self):
        inp = self.inputs[0].eval()
        if self.output_type == "STRING":
            self.outputs[0].code = f"str({inp})"
        elif self.output_type == "INT":
            self.outputs[0].code = f"int({inp})"
        elif self.output_type == "FLOAT":
            self.outputs[0].code = f"float({inp})"
