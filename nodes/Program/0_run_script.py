import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RunScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunScriptNode"
    bl_label = "Run Script"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.2,0.2,0.2)
    }
    
    
    script: bpy.props.StringProperty()


    def on_create(self,context):
        self.add_execute_input("Execute")
        self.add_execute_output("Execute")
        
        
    def draw_node(self,context,layout):
        layout.prop_search(self,"script",bpy.data,"texts",text="Script")


    def code_evaluate(self, context, touched_socket):

        script = [""]
        if self.script and self.script in bpy.data.texts:
            script = bpy.data.texts[self.script]
            script = script.as_string()
            script = script.split("\n")
            for i in range(len(script)):
                script[i] = script[i] + "\n"
            
        return {
            "code": f"""
                    pass # {self.script} Script Start
                    {self.list_blocks(script,5)}
                    pass # {self.script} Script End
                    
                    {self.outputs[0].block(5)}
                    """
        }