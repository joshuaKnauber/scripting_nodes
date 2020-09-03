import bpy
import os
import gpu
from gpu_extras.batch import batch_for_shader
import bgl
from .drawing_ops import DrawingFuncs



tutorial_images = [
    "tut1.jpg",
    "tut2.jpg",
    "tut3.jpg",
    "tut4.jpg",
    "tut5.jpg",
]

def get_tut_images():
    global tutorial_images
    return tutorial_images



class SN_OT_NextTutorial(bpy.types.Operator):
    bl_idname = "scripting_nodes.next_tutorial"
    bl_label = "Next Step"
    bl_description = "Shows the next step in the tutorial"
    bl_options = {"REGISTER","INTERNAL"}

    previous: bpy.props.BoolProperty()

    def execute(self, context):
        if self.previous:
            context.scene.sn_properties.tut_index -= 1
        else:
            context.scene.sn_properties.tut_index += 1
        return {"FINISHED"}



class SN_DrawTutorial(DrawingFuncs, bpy.types.Operator):
    bl_idname = "scripting_nodes.draw_tutorial"
    bl_label = "Draw Tutorial"
    bl_description = "Draws the tutorial"
    bl_options = {"REGISTER","INTERNAL"}

    def close(self, context):
        bpy.types.SpaceNodeEditor.draw_handler_remove(self.handler, 'WINDOW')
        self.remove_imgs()
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

    def modal(self, context, event):
        if not context.area or not context.area.type == "NODE_EDITOR":
            context.scene.sn_properties.show_tutorial = False
            return self.close(context)
        elif context.area.type == "NODE_EDITOR" and not context.space_data.tree_type == "ScriptingNodesTree":
            context.scene.sn_properties.show_tutorial = False
            return self.close(context)

        if event.type == "ESC" or not context.scene.sn_properties.show_tutorial:
            context.scene.sn_properties.show_tutorial = False
            return self.close(context)

        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            m_x = event.mouse_region_x
            m_y = self.get_width_height(context)[1] + event.mouse_region_y
            for button in self.buttons:
                if m_x >= button["minX"] and m_x <= button["maxX"]:
                    if m_y >= button["minY"] and m_y <= button["maxY"]:

                        if button["url"]:
                            bpy.ops.wm.url_open(url=button["url"])
                        if button["callback"]:
                            button["callback"]()
                        if button["close"]:
                            context.scene.sn_properties.show_tutorial = False

        return {'PASS_THROUGH'}

    def remove_imgs(self):
        for img in get_tut_images():
            if img in bpy.data.images:
                bpy.data.images.remove(bpy.data.images[img])

    def load_image(self,context,IMAGE_NAME):
        self.remove_imgs()
        image = bpy.data.images.load(os.path.join(os.path.dirname(__file__),"tut_imgs",IMAGE_NAME),check_existing=True)
        width, height = self.get_width_height(context)
        image_height = height - 100
        image_width = image_height * 4/3

        while image_width >= width - 100 and not image_width < 200:
            image_height -= 10
            image_width = image_height * 4/3

        self.image_shader = gpu.shader.from_builtin('2D_IMAGE')
        x = (width-image_width)/2
        y = (height-image_height)/2
        self.image_batch = batch_for_shader(
            self.image_shader, 'TRI_FAN',
            {
                "pos": ( (x, y), (x+image_width, y), (x+image_width, y+image_height), (x, y+image_height) ),
                "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
            },
        )

        if image.gl_load():
            raise Exception()
        return image

    def draw_callback(self, context):
        self.buttons.clear()
        if context.space_data.tree_type == "ScriptingNodesTree":
            scale = context.scene.sn_properties.tutorial_scale
            width, height = self.get_width_height(context)
            padding = 2 * scale
            outline_width = 1.5 * scale
            close_button_size = 20 * scale
            close_cross_width = 5 * scale
            font_size_title = int(14 * scale)
            font_size_text = int(13 * scale)
            font_size_python = int(12 * scale)

            # draw outline
            self.draw_outline(context,outline_width,padding)

            # draw close button
            self.draw_close_setup(context,close_button_size,padding,outline_width,close_cross_width)
        
            # draw tutorial title
            self.draw_text("<serpens>SERPENS</> - Tutorial",font_size_title,(padding+10,padding+10),0)

            # draw tutorial image
            if context.scene.sn_properties.tut_index <= len(get_tut_images())-1:
                image = self.load_image(context,get_tut_images()[context.scene.sn_properties.tut_index])
                bgl.glActiveTexture(bgl.GL_TEXTURE0)
                bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)

                self.image_shader.bind()
                self.image_shader.uniform_int("image", 0)
                self.image_batch.draw(self.image_shader)