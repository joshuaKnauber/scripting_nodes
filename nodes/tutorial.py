import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader
import os
from .base_node import SN_ScriptingBaseNode



tutorial = [
    {
        "image": "size_adjust.jpg"
    },
    {
        "image": "get_started.jpg"
    },
    {
        "image": "what_is_it.jpg"
    },
    {
        "image": "structure.jpg"
    },
    {
        "image": "graphs.jpg"
    },
    {
        "image": "bookmark.jpg"
    },
    {
        "image": "switch_addon.jpg"
    },
    {
        "image": "links.jpg"
    },
    {
        "image": "compile.jpg"
    },
    {
        "image": "panel_start.jpg",
        "nodes": [
                    {"idname": "SN_AddToPanelNode",
                     "name": "First Add To Panel",
                     "offset_x": 0,
                     "offset_y": -150}
                ],
    },
    {
        "image": "label.jpg",
        "nodes": [
                    {"name": "First Add To Panel"},
                    {"idname": "SN_LabelNode",
                     "name": "First Label",
                     "offset_x": 300,
                     "offset_y": -150}
                ],
        "links": [
                    {"out_name":"First Add To Panel",
                    "out_socket":0,
                    "in_name":"First Label",
                    "in_socket":0}
        ]
    },
    {
        "image": "seeing_the_label.jpg",
        "nodes": None,
        "links": None
    },
    {
        "image": "adventure.jpg",
        "adventure": True
    },
    {
        "image": "interface.jpg",
        "sockets": [
            "self.add_interface_output('Interface')",
            "self.add_interface_input('Interface')",
        ]
    },
    {
        "image": "execute.jpg",
        "sockets": [
            "self.add_execute_output('Execute')",
            "self.add_execute_input('Execute')",
        ]
    },
    {
        "image": "function.jpg"
    },
    {
        "image": "data.jpg"
    },
    {
        "image": "variables.jpg"
    },
    {
        "image": "get_property.jpg",
        "nodes": [
                    {"idname": "SN_GetPropertyNode",
                     "name": "Get First Property",
                     "offset_x": 0,
                     "offset_y": -150}
                ],
    },
    {
        "image": "blend_data.jpg"
    },
    {
        "image": "properties.jpg"
    },
    {
        "image": "operator.jpg"
    },
    {
        "image": "custom_files.jpg"
    },
    {
        "image": "save.jpg"
    },
    {
        "image": "marketplace.jpg"
    },
    {
        "image": "packages.jpg"
    },
    {
        "image": "console.jpg"
    },
    {
        "image": "have_fun.jpg"
    },
]



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


shader = None
batch = None
image = None
handler = None


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


class SN_TutorialNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TutorialNode"
    bl_label = "Tutorial"
    bl_icon = "HELP"
    bl_width_default = 212
    
    node_options = {
        "default_color": (0.15,0.15,0.15),
    }
    
    show_settings: bpy.props.BoolProperty(default=False,name="Show Settings",description="Show the settings")
    
    
    chapters = [
        ("Overview", "what_is_it"),
        ("Nodes", "panel_start"),
        ("Interface", "interface"),
        ("Execute", "execute"),
        ("Functions", "function"),
        ("Data", "data"),
        ("Variables", "variables"),
        ("Blend Data", "blend_data"),
        ("Properties", "properties"),
        ("Operators", "operator"),
        ("Assets", "custom_files"),
        ("Export", "save"),
        ("Marketplace", "marketplace"),
        ("Packages", "packages"),
        ("Console", "console"),
    ]
    
    
    def remove_images(self):
        for step in tutorial:
            if step["image"] in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[step["image"]])
                
                
    def remove_sockets(self):
        self.inputs.clear()
        self.outputs.clear()
                
                
    def update_sockets(self):
        if not "sockets" in tutorial[self.index]:
            self.remove_sockets()
        elif tutorial[self.index]["sockets"] != None:
            self.remove_sockets()

            for socket in tutorial[self.index]["sockets"]:
                exec(socket)
                
                
    def remove_nodes(self):
        next_nodes = []
        if "nodes" in tutorial[self.index]:
            for node in tutorial[self.index]["nodes"]:
                next_nodes.append(node["name"])
        for node in self.node_tree.nodes:
            if not node == self and not node.name in next_nodes:
                self.node_tree.nodes.remove(node)
            
    
    def update_nodes(self):
        if not "nodes" in tutorial[self.index]:
            self.remove_nodes()
        elif tutorial[self.index]["nodes"] != None:
            self.remove_nodes()
        
            for node in tutorial[self.index]["nodes"]:
                if not node["name"] in self.node_tree.nodes:
                    new_node = self.node_tree.nodes.new(node["idname"])
                    new_node.name = node["name"]
                    new_node.location = (self.location[0]+node["offset_x"],self.location[1]+node["offset_y"])
            
    
    def remove_links(self):
        for link in self.node_tree.links:
            self.node_tree.links.remove(link)
            
            
    def update_links(self):
        if not "links" in tutorial[self.index]:
            self.remove_links()
        elif tutorial[self.index]["links"] != None:
            self.remove_links()

            for link in tutorial[self.index]["links"]:
                if link["out_name"] == "self":
                    out_socket = self.outputs[link["out_socket"]]
                else:
                    out_socket = self.node_tree.nodes[link["out_name"]].outputs[link["out_socket"]]
                if link["in_name"] == "self":
                    in_socket = self.inputs[link["in_socket"]]
                else:
                    in_socket = self.node_tree.nodes[link["in_name"]].inputs[link["in_socket"]]
                self.node_tree.links.new(out_socket,in_socket)
    
    
    def update_shader(self,context):
        self.remove_images()
        dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"assets","tutorial")
        img = bpy.data.images.load(os.path.join(dir_path, tutorial[self.index]["image"]),check_existing=True)
        img.colorspace_settings.name = "Linear"
        load_shader(img,self.x,self.y,self.size)
        self.update_sockets()
        self.update_nodes()
        self.update_links()
    
    
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
        for i, step in enumerate(tutorial):
            for el in self.chapters:
                if step["image"] == el[1] + ".jpg":
                    current_chapter = el[0]
            if i == self.index:
                return current_chapter
        return current_chapter
    

    def draw_node(self,context,layout):
        row = layout.row()
        row.alignment = "CENTER"
        row.label(text=self.current_chapter())
        
        if "adventure" in tutorial[self.index]:
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
            col.enabled = self.index < len(tutorial)-1
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
        
        if self.index == 1:            
            layout.label(text="Chapters")
            col = layout.column(align=True)
            col.scale_y = 1.2
            for index, chapter in enumerate(self.chapters):
                op = col.operator("sn.set_tutorial",text=str(index+1) + " | " + chapter[0])
                op.node = self.name
                for i, step in enumerate(tutorial):
                    if step["image"] == chapter[1] + ".jpg":
                        op.index = i
                        break
                    
        elif tutorial[self.index]["image"] == "packages.jpg":
            row = layout.row()
            row.operator("wm.url_open",text="See Docs",icon="URL").url = "https://joshuaknauber.github.io/visual_scripting_addon_docs/visual_scripting_docs/site/"