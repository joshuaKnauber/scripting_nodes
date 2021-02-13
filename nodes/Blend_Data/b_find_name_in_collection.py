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
        if link.to_socket == self.inputs[0]:
            self.collection_error = False
            if link.from_socket.subtype == "COLLECTION":
                self.outputs[0].data_type = link.from_socket.data_type
                self.outputs[0].data_identifier = link.from_socket.data_identifier
                self.outputs[0].data_name = link.from_socket.data_name
                for link in self.outputs[0].links:
                    link.to_socket.node.on_link_insert(link)
            else:
                self.collection_error = True


    def on_create(self,context):
        inp = self.add_blend_data_input("Blend Data")
        inp.mirror_name = True
        inp.subtype = "COLLECTION"
        self.add_string_input("Name")
        self.add_blend_data_output("Data Block")
        self.add_integer_output("Data Block Index").set_default(-1)
        self.add_boolean_output("Data Block Exists").set_default(False)
        
        
    def draw_node(self,context,layout):
        if self.collection_error:
            layout.label(text="Connect data collection",icon="ERROR")


    def code_evaluate(self, context, touched_socket):
        
        if self.inputs[0].links:
            if touched_socket == self.outputs[0]: # data block
                return {"code": f"{self.inputs[0].code()}[{self.inputs[1].code()}]"}

            elif touched_socket == self.outputs[1]: # index int
                return {"code": f"{self.inputs[0].code()}.find({self.inputs[1].code()})"}
                
            else: # exists bool
                return {"code": f"{self.inputs[0].code()}.find({self.inputs[1].code()}) != -1"}
        else:
            self.add_error("No blend data", "Blend data input is not connected", True)
            if touched_socket == self.outputs[0]: # data block
                return {"code": "None"}
            elif touched_socket == self.outputs[1]: # index int
                return {"code": "0"}
            else:
                return {"code": "False"}