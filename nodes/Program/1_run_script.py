import bpy
import os
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup




class SN_RunScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunScriptNode"
    bl_label = "Run Script"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "always_recompile": True
    }
    
    
    script: bpy.props.StringProperty(update=SN_ScriptingBaseNode.auto_compile)
    
    script_source: bpy.props.EnumProperty(name="Source",
                                          description="Source of the script file",
                                          items=[("TEXT","Text","Text"),("FILE","File","File")],
                                          update=SN_ScriptingBaseNode.auto_compile)
    
    path: bpy.props.StringProperty(name="Path",
                                   description="Path to the script file",
                                   subtype="FILE_PATH",
                                   update=SN_ScriptingBaseNode.auto_compile)


    def on_create(self,context):
        self.add_execute_input("Run Script")
        self.add_execute_output("Execute").mirror_name = True
        
        
    def draw_node(self,context,layout):
        if not hasattr(self, "script_source"):
            row = layout.row(align=True)
            row.prop_search(self,"script",bpy.data,"texts",text="Script")

        else:
            layout.prop(self, "script_source", expand=True)
            row = layout.row(align=True)
            if self.script_source == "TEXT":
                row.prop_search(self,"script",bpy.data,"texts",text="Script")
            else:
                row.prop(self, "path")


    def code_evaluate(self, context, touched_socket):

        script = [""]
        if getattr(self, "script_source", "TEXT") == "TEXT" and (self.script and self.script in bpy.data.texts):
            script = bpy.data.texts[self.script]
            script = script.as_string()
            script = script.split("\n")
            for i in range(len(script)): 
                script[i] = script[i] + "\n"
                
        elif getattr(self,"path", "") and os.path.exists(bpy.path.abspath(self.path)):
            with open(bpy.path.abspath(self.path), "r") as script_file:
                script = script_file.readlines()
        
        else:
            self.add_error("No Valid Script","You do not have a valid script selected")

        return {
            "code": f"""
                    pass # {self.script} Script Start
                    {self.list_code(script,5)}
                    pass # {self.script} Script End
                    
                    {self.outputs[0].code(5)}
                    """
        }