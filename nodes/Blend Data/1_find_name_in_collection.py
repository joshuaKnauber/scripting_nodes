import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_FindInDataCollectionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FindInDataCollectionNode"
    bl_label = "Find In Data Collection"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    collection_error: bpy.props.BoolProperty(default=False)
    
    
    def on_link_insert(self,link):
        self.collection_error = False
        if link.to_socket == self.inputs[0]:
            if link.from_socket.collection:
                self.outputs[0].data_type = link.from_socket.data_type
            else:
                self.collection_error = True


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").copy_name = True
        self.add_string_input("Name")
        self.add_blend_data_output("Data Block")
        self.add_integer_output("Data Block Index").set_default(-1)
        self.add_boolean_output("Data Block Exists").set_default(False)
        
        
    def draw_node(self,context,layout):
        if self.collection_error:
            layout.label(text="Connect data collection",icon="ERROR")


    def code_evaluate(self, context, touched_socket):

        if touched_socket == self.outputs[0]: # data block
            return {"code": f"{self.inputs[0].value}[{self.inputs[1].value}]"}

        elif touched_socket == self.outputs[1]: # index int
            return {"code": f"{self.inputs[0].value}.find({self.inputs[1].value})"}
            
        else: # exists bool
            return {"code": f"{self.inputs[0].value}.find({self.inputs[1].value}) != -1"}

        
#TODO function for node to choose one value based on bool | like if but inline with function