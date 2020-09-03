import bpy
import os
import gpu
from gpu_extras.batch import batch_for_shader
import blf
import bgl
from ..handler.text_colors import TextColorHandler



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



class SN_DrawTutorial(bpy.types.Operator):
    bl_idname = "scripting_nodes.draw_tutorial"
    bl_label = "Draw Tutorial"
    bl_description = "Draws the tutorial"
    bl_options = {"REGISTER","INTERNAL"}

    def invoke(self, context, event):
        self.buttons = []
        self.handler = bpy.types.SpaceNodeEditor.draw_handler_add(self.draw_callback,(context,),'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def close(self, context):
        bpy.types.SpaceNodeEditor.draw_handler_remove(self.handler, 'WINDOW')
        self.remove_imgs()
        context.area.tag_redraw()
        return {'FINISHED'}

    def modal(self, context, event):
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

    def get_width_height(self, context):
        width = context.area.width
        height = context.area.height
        
        for region in context.area.regions:
            if region.type == "UI":
                width -= region.width
            elif region.type == "HEADER":
                height -= region.height

        return width, height

    def create_outline(self, context, padding):
        width, height = self.get_width_height(context)
        
        vertices = (
            (padding, padding), (padding, height-padding),
            (width-padding, height-padding), (width-padding, padding),
        )
        indices = (
            (0, 1), (1, 2), (2, 3), (3, 0)
        )

        self.outline_batch = batch_for_shader(self.white_shader, 'LINES', {"pos": vertices}, indices=indices)

    def create_close_button(self, context, size, padding):
        width, height = self.get_width_height(context)

        vertices = (
            (width-size-padding, height-padding), (width-padding, height-padding),
            (width-padding, height-size-padding), (width-size-padding, height-size-padding),
        )
        indices = (
            (0, 1, 2), (0, 3, 2)
        )

        self.close_batch = batch_for_shader(self.white_shader, 'TRIS', {"pos": vertices}, indices=indices)

        return vertices

    def create_close_cross(self, context, size, padding, inner_padding):
        width, height = self.get_width_height(context)

        vertices = (
            (width-size-padding+inner_padding, height-padding-inner_padding), (width-padding-inner_padding, height-size-padding+inner_padding),
            (width-size-padding+inner_padding, height-size-padding+inner_padding), (width-padding-inner_padding, height-padding-inner_padding),
        )
        indices = (
            (0, 1), (2, 3)
        )

        self.close_cross_batch = batch_for_shader(self.black_shader, 'LINES', {"pos": tuple(vertices)}, indices=tuple(indices))

    def process_text(self, text):
        processed = []
        split_text = text.split("</>")

        for index, part in enumerate(split_text):
            is_valid = False
            part = part.split(">")

            if len(part) > 1:
                colored_text = part[-1]
                if len(part[-2].split("<")) > 1:
                    color = part[-2].split("<")[-1]
                    white_text = ("<").join(part[-2].split("<")[:-1])
                    is_valid = True
                elif len(part[-2].split("<")) == 1:
                    color = part[-2].split("<")[0]
                    white_text = ""
                    is_valid = True

            if not is_valid:
                processed.append( ((">").join(part), (1,1,1,1)) )
            else:
                color = TextColorHandler().color_by_name(color)
                processed.append( (white_text, (1,1,1,1)) )
                processed.append( (colored_text, color) )

        return processed


    def draw_text(self,text,font_size,position,font_id):
        processed = self.process_text(text)
        x_offset = 0
        y_offset = 0
        for snippet in processed:
            blf.size(font_id, font_size, 72)
            blf.position(font_id, position[0] + x_offset, position[1], 0)
            blf.color(font_id, snippet[1][0], snippet[1][1], snippet[1][2], 1.0)
            blf.draw(font_id, snippet[0])
            width, height = blf.dimensions(font_id, snippet[0])
            x_offset += width
            y_offset = max(y_offset,height)
        return y_offset

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
            self.white_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            self.white_shader.bind()
            self.white_shader.uniform_float("color", (1, 1, 1, 1.0))

            self.create_outline(context, padding)
            bgl.glLineWidth(outline_width)
            self.outline_batch.draw(self.white_shader)

            # draw close button
            vertices = self.create_close_button(context, close_button_size, padding-outline_width/2)
            self.close_batch.draw(self.white_shader)
            self.buttons.append({
                "minX": min(vertices, key = lambda t: t[0])[0],
                "minY": min(vertices, key = lambda t: t[1])[1],
                "maxX": max(vertices, key = lambda t: t[0])[0],
                "maxY": max(vertices, key = lambda t: t[1])[1],
                "close": True,
                "url": None,
                "callback": None
            })

            # draw close cross
            self.black_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            self.black_shader.bind()
            self.black_shader.uniform_float("color", (0, 0, 0, 1.0))

            self.create_close_cross(context, close_button_size, padding-outline_width/2, 4)
            bgl.glLineWidth(close_cross_width)
            self.close_cross_batch.draw(self.black_shader)
        
            # draw tutorial title
            self.draw_text("<serpens>SERPENS</> - Tutorial",font_size_title,(padding+10,padding+10),0)


            # draw tutorial image
            image = self.load_image(context,get_tut_images()[context.scene.sn_properties.tut_index])
            bgl.glActiveTexture(bgl.GL_TEXTURE0)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)

            self.image_shader.bind()
            self.image_shader.uniform_int("image", 0)
            self.image_batch.draw(self.image_shader)