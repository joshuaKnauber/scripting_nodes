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
    
    
    
class SN_OT_MoveTutorial(bpy.types.Operator):
    bl_idname = "sn.move_tutorial"
    bl_label = "Move Tutorial"
    bl_description = "Changes the tutorial step"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    forward: bpy.props.BoolProperty()
    node: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        node.index = node.index + 1 if self.forward else node.index - 1
        node.node_tree.backdrop_image = bpy.data.images[1]
        return {"FINISHED"}



class SN_TutorialNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TutorialNode"
    bl_label = "Tutorial"
    bl_icon = "HELP"
    bl_width_default = 212
    
    node_options = {
        "default_color": (0.15,0.15,0.15),
    }
    
    
    index: bpy.props.IntProperty(default=0,min=0)
    
    tut_textures = []
    

    def on_create(self,context):
        if not self.tut_textures:
            dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"assets","tutorial")
            tut_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
            for img in tut_files:
                tex = bpy.data.textures.new("."+img, "IMAGE")
                img = bpy.data.images.load(os.path.join(dir_path, img))
                img.name = "." + img.name
                tex.image = img
                tex.use_fake_user = True
                self.tut_textures.append(tex)
        
        
    def on_free(self):
        for tex in self.tut_textures:
            bpy.data.images.remove(tex.image)
            bpy.data.textures.remove(tex)
        self.tut_textures.clear()
    

    def draw_node(self,context,layout):   
        row = layout.row(align=True)
        col = row.column(align=True)
        col.scale_y = 2
        col.enabled = self.index > 0
        op = col.operator("sn.move_tutorial",text="",icon="TRIA_LEFT")
        op.forward = False
        op.node = self.name
        row.template_icon_view(bpy.data.textures[self.index])
        col = row.column(align=True)
        col.scale_y = 2
        col.enabled = self.index < len(self.tut_textures)-1
        op = col.operator("sn.move_tutorial",text="",icon="TRIA_RIGHT")
        op.forward = True
        op.node = self.name
        layout.prop(self,"index")
