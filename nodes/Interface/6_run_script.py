import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup




class SN_RunScriptInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunScriptInterfaceNode"
    bl_label = "Run Interface Script"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3)
    }
    
    
    script: bpy.props.StringProperty(update=SN_ScriptingBaseNode.auto_compile)


    def on_create(self,context):
        self.add_interface_input("Interface").mirror_name = True
    

    def draw_node(self,context,layout):
        layout.label(text="Use 'sn_layout' in your script!")
        row = layout.row(align=True)
        row.prop_search(self,"script",bpy.data,"texts",text="Script")
    
    
    def code_evaluate(self, context, touched_socket):

        script = [""]
        if self.script and self.script in bpy.data.texts:
            script = bpy.data.texts[self.script]
            script = script.as_string()
            script = script.split("\n")
            for i in range(len(script)):
                script[i] = script[i] + "\n"
        
        else:
            self.add_error("No Valid Script","You do not have a valid script selected")

        return {
            "code": f"""
                    sn_layout = {touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)}
                    # {self.script} Script Start
                    {self.list_code(script,5)}
                    pass # {self.script} Script End
                    """
        }