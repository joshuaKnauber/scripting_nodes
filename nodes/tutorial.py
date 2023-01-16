import bpy
import re
import gpu
import bgl
from gpu_extras.batch import batch_for_shader
import os
from .base_node import SN_ScriptingBaseNode



class SN_OT_StartTutorial(bpy.types.Operator):
    bl_idname = "sn.start_tutorial"
    bl_label = "Start Tutorial"
    bl_description = "Adds the tutorial node to your node tree"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        tree = context.space_data.node_tree
        tree.nodes.new("SN_TutorialNode")
        return {"FINISHED"}
    
    
    
class SN_OT_EndTutorial(bpy.types.Operator):
    bl_idname = "sn.end_tutorial"
    bl_label = "End Tutorial"
    bl_description = "Ends the tutorial"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty()

    def execute(self, context):
        tree = context.space_data.node_tree
        tree.nodes.remove(tree.nodes[self.node])
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
    
    
    
class SN_OT_SetTutorial(bpy.types.Operator):
    bl_idname = "sn.set_tutorial"
    bl_label = "Set Tutorial"
    bl_description = "Changes the tutorial step"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty()
    node: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        node.index = self.index
        return {"FINISHED"}


def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))[0]

def load_images():
    images = []
    for file in os.listdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "tutorial")):
        if file.split(".")[-1] == "jpg":
            images.append(file)
    images.sort(key=num_sort)
    return images

shader = None
batch = None
image = None
handler = None

images = load_images()



def load_shader(img, x, y, size):
    global shader
    global batch
    global image
    
    image = img
    
    width, height = size, int(size*0.6)

    x -= width//2
    y -= height//2

    shader = gpu.shader.from_builtin('2D_IMAGE')
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {
            "pos": ((x, y), (x+width, y), (x+width, y+height), (x, y+height)),
            "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
        },
    )

    if image.gl_load():
        raise Exception()



def draw():
    global shader
    global batch
    global image
    
    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    try:
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)
        shader.bind()
        shader.uniform_int("image", 0)
        batch.draw(shader)

    except:
        bpy.types.SpaceNodeEditor.draw_handler_remove(handler, 'WINDOW')



class SN_TutorialNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_TutorialNode"
    bl_label = "Tutorial"
    bl_icon = "HELP"
    bl_width_default = 220
    
    show_settings: bpy.props.BoolProperty(default=False,
                                        name="Show Settings",
                                        description="Show the settings")
    
    
    chapters = [
        ("Overview", "0.jpg"),
        ("UI", "4.jpg"),
        ("Nodes", "6.jpg"),
        ("Interface", "9.jpg"),
        ("Execute", "10.jpg"),
        ("Data", "12.jpg"),
        ("Variables", "13.jpg"),
        ("Blender Data", "14.jpg"),
        ("Properties", "16.jpg"),
        ("Operators", "17.jpg"),
        ("Export", "18.jpg"),
    ]
    
    
    def remove_images(self):
        for image in images:
            if image in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[image])
                
    
    def update_shader(self,context):
        self.remove_images()
        dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"assets","tutorial")
        img = bpy.data.images.load(os.path.join(dir_path, images[self.index]),check_existing=True)
        img.colorspace_settings.name = "Linear"
        load_shader(img,self.x,self.y,self.size)
    
    
    x: bpy.props.IntProperty(default=100, update=update_shader, min=0)
    y: bpy.props.IntProperty(default=100, update=update_shader, min=0)
    size: bpy.props.IntProperty(default=400, update=update_shader, min=10)
    

    index: bpy.props.IntProperty(default=0, update=update_shader)
    

    def on_create(self,context):
        global handler
        
        self.x = bpy.context.region.width//2
        self.y = bpy.context.region.height//2
        self.size = int(bpy.context.region.height * 0.8)
        
        self.index = 0
        if not handler:
            handler = bpy.types.SpaceNodeEditor.draw_handler_add(draw, (), 'WINDOW', 'BACKDROP')
        
        
    def on_free(self):
        global handler
        
        self.index = 0
        bpy.types.SpaceNodeEditor.draw_handler_remove(handler, 'WINDOW')
        handler = None
        self.remove_images()
        
        
    def current_chapter(self):
        current_chapter = "Tutorial"
        for i, image in enumerate(images):
            for el in self.chapters:
                if image == el[1]:
                    current_chapter = el[0]
            if i == self.index:
                return current_chapter
        return current_chapter
    

    def draw_node(self, context, layout):
        row = layout.row()
        row.alignment = "CENTER"
        row.label(text=self.current_chapter())
        
        CHAPTER_INDEX = 1
        ADVENTURE_INDEX = 8
        
        if self.index == ADVENTURE_INDEX:
            col = layout.column()
            col.scale_y = 2
            op = col.operator("sn.move_tutorial",text="Keep Going!",icon="OUTLINER_DATA_LIGHT")
            op.node = self.name
            op.forward = True
            col.operator("sn.end_tutorial",text="ADVENTURE!!!",icon="OUTLINER_DATA_ARMATURE").node = self.name
            
        else:
            row = layout.row(align=True)
            row.scale_y = 1.2
            col = row.column(align=True)
            col.enabled = self.index > 1
            op = col.operator("sn.set_tutorial",text="",icon="REW")
            op.node = self.name
            op.index = 1
            col = row.column(align=True)
            col.enabled = self.index > 0
            op = col.operator("sn.move_tutorial",icon="TRIA_LEFT",text="Previous")
            op.node = self.name
            op.forward = False
            col = row.column(align=True)
            col.enabled = self.index < len(images)-1
            op = col.operator("sn.move_tutorial",icon="TRIA_RIGHT",text="Next")
            op.node = self.name
            op.forward = True
            row.operator("sn.end_tutorial",text="",icon="HANDLETYPE_VECTOR_VEC").node = self.name
            
            if self.index > 0:
                layout.prop(self,"show_settings",text="Image Size",icon="TRIA_DOWN" if self.show_settings else "TRIA_RIGHT",emboss=False)
            
            if self.index == 0 or self.show_settings:
                col = layout.column(align=True)
                col.scale_y = 1.2
                row = col.row(align=True)
                col.prop(self,"size",text="Size")
                row.prop(self,"x",text="X")
                row.prop(self,"y",text="Y")
            
        layout.operator("wm.url_open",text="See Docs",icon="URL").url = "https://joshuaknauber.notion.site/Serpens-Documentation-d44c98df6af64d7c9a7925020af11233"
        
        if self.index == CHAPTER_INDEX:            
            layout.label(text="Chapters")
            col = layout.column(align=True)
            col.scale_y = 1.2
            for index, chapter in enumerate(self.chapters):
                op = col.operator("sn.set_tutorial",text=str(index+1) + " | " + chapter[0])
                op.node = self.name
                for i, image in enumerate(images):
                    if image == chapter[1]:
                        op.index = i
                        break
