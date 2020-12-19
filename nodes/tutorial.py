import bpy
from ..node_tree.base_node import SN_ScriptingBaseNode
import os



class SN_OT_StartTutorial(bpy.types.Operator):
    bl_idname = "sn.start_tutorial"
    bl_label = "Start Tutorial"
    bl_description = "Adds the tutorial node to your node tree"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        tree = context.space_data.node_tree
        tree.nodes.new("SN_TutorialNode")
        return {"FINISHED"}



class SN_TutorialNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TutorialNode"
    bl_label = "Tutorial"
    bl_icon = "GRAPH"
    bl_width_default = 300
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    

    def on_create(self,context):
        dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"assets","tutorial")
        tut_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
            
        
    def on_free(self):
        pass
    

    def draw_node(self,context,layout):   
        pass