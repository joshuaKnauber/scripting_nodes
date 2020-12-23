import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_OT_GetPythonName(bpy.types.Operator):
    bl_idname = "sn.get_python_name"
    bl_label = "Get Python Name"
    bl_description = "Get the python name for the name of a  variable, function, etc."
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    def update_name(self,context):
        node_instance = SN_ScriptingBaseNode()
        self.py_name = node_instance.get_python_name(self.name)
    
    name: bpy.props.StringProperty(default="",options={"SKIP_SAVE"},update=update_name)
    py_name: bpy.props.StringProperty(options={"SKIP_SAVE"})

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self,context):
        self.layout.label(text="Enter name here:")
        self.layout.prop(self,"name",text="")
        self.layout.separator()
        self.layout.label(text="Copy python name here:")
        self.layout.prop(self,"py_name",text="")
    
    def invoke(self,context,event):
        return context.window_manager.invoke_popup(self,width=300)




class SN_RunScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunScriptNode"
    bl_label = "Run Script"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3)
    }
    
    
    script: bpy.props.StringProperty()


    def on_create(self,context):
        self.add_execute_input("Execute")
        self.add_execute_output("Execute")
        
        
    def draw_node(self,context,layout):
        row = layout.row(align=True)
        row.prop_search(self,"script",bpy.data,"texts",text="Script")
        row.operator("sn.get_python_name",text="",icon="UV_SYNC_SELECT")


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
                    pass # {self.script} Script Start
                    {self.list_blocks(script,5)}
                    pass # {self.script} Script End
                    
                    {self.outputs[0].block(5)}
                    """
        }