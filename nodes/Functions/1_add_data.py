import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_AddDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddDataNode"
    bl_label = "Create Blend Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    current_data_type: bpy.props.StringProperty(default="")
    
    
    def add_function_inputs(self,data_type):
        for i in range(len(self.inputs)-1,-1,-1):
            if not i < 2:
                self.inputs.remove(self.inputs[i])
        print("dir(bpy.types."+data_type+".bl_rna.functions)")
        if "new" in eval("dir(bpy.types."+data_type+".bl_rna.functions)"):
            for prop in eval("bpy.types."+data_type+".bl_rna.functions['new'].parameters"):
                print(prop)
    
    
    def on_link_insert(self,link):
        if link.to_socket == self.inputs[1] and not link.from_socket.data_type == self.current_data_type:
            self.inputs[1].data_type = link.from_socket.data_type
            if len(self.outputs) == 1:
                self.add_blend_data_output("New Data")
            out = self.outputs[1]
            out.data_type = link.from_socket.data_type
            self.current_data_type = link.from_socket.data_type
            self.add_function_inputs(link.from_socket.data_type)


    def on_create(self,context):
        self.add_execute_input("Execute").copy_name = True
        inp = self.add_blend_data_input("Blend Data")
        inp.copy_name = True
        inp.collection = True
        self.add_execute_output("Execute")


    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"""
                    {self.inputs[1].value}.new({self.inputs[2].value})
                    {self.outputs[0].block(5)}
                    """
        }
        #TODO