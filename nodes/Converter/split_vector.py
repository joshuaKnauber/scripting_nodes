import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_SplitVectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SplitVectorNode"
    bl_label = "Split Vector"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def update_vector_type(self,context):
        types = {"FLOAT":"SN_FloatSocket","INTEGER":"SN_IntegerSocket","BOOLEAN":"SN_BooleanSocket"}
        if self.vector_type != self.inputs[0].socket_type:
            for inp in self.inputs:
                self.change_socket_type(inp,types[self.vector_type])
            for out in self.outputs:
                self.change_socket_type(out,types[self.vector_type])
        for inp in self.inputs:
            if self.use_four:
                inp.subtype = "VECTOR4"
            else:
                inp.subtype = "VECTOR3"
        if self.use_four and len(self.outputs) == 3:
            self.add_output(self.outputs[0].bl_idname,"W")
        if not self.use_four and len(self.outputs) == 4:
            self.outputs.remove(self.outputs[-1])
    
    
    vector_type: bpy.props.EnumProperty(name="Type",
                                        description="The type of vector that should be used",
                                        items=[("FLOAT","Float","Float Vector"),
                                               ("INTEGER","Integer","Integer Vector"),
                                               ("BOOLEAN","Boolean","Boolean Vector")],
                                        update=update_vector_type)
    
    use_four: bpy.props.BoolProperty(name="Vector 4",
                                     description="Use four values for the vector",
                                     update=update_vector_type)
    

    def on_create(self,context):
        self.add_float_input("Vector").subtype = "VECTOR3"
        
        self.add_float_output("X")
        self.add_float_output("Y")
        self.add_float_output("Z")
        
        
    def draw_node(self,context,layout):
        layout.prop(self,"vector_type",expand=True)
        layout.prop(self,"use_four")
        

    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"{self.inputs[0].code()}[{self.outputs.find(touched_socket.default_text)}]"
        }