import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_circle_2d
import blf
import bgl
from ..handler.text_colors import TextColorHandler


class DrawingFuncs:

    def invoke(self, context, event):
        self.buttons = []
        self.handler = bpy.types.SpaceNodeEditor.draw_handler_add(self.draw_callback,(context,),'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

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


    def draw_outline(self, context, outline_width, padding):
        self.white_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        self.white_shader.bind()
        self.white_shader.uniform_float("color", (1, 1, 1, 1.0))

        # self.create_outline(context, padding)
        # bgl.glLineWidth(outline_width)
        # self.outline_batch.draw(self.white_shader)


    def draw_close_setup(self,context,close_button_size,padding,outline_width,close_cross_width):
        # vertices = self.create_close_button(context, close_button_size, padding-outline_width/2)
        # self.close_batch.draw(self.white_shader)
        vertices = self.create_close_button(context, close_button_size, padding+10)
        buttonData = {
            "minX": min(vertices, key = lambda t: t[0])[0],
            "minY": min(vertices, key = lambda t: t[1])[1],
            "maxX": max(vertices, key = lambda t: t[0])[0],
            "maxY": max(vertices, key = lambda t: t[1])[1],
            "close": True,
            "url": None,
            "callback": None
        }
        self.buttons.append(buttonData)

        # bgl.glLineWidth(2)
        # for i in range(1,int(close_button_size//2)):
        #     draw_circle_2d( (buttonData["minX"]+close_button_size//2,buttonData["minY"]+close_button_size//2), (0.9,0.15,0.25,1), max(1,close_button_size//2-i), 32)

        scale = context.scene.sn_properties.tutorial_scale
        blf.size(0, int(13*scale), 72)
        width, height = blf.dimensions(0, "Esc")
        self.draw_text("<subtext>Esc</>", int(13*scale), (buttonData["minX"]-width-int(10*scale) ,buttonData["minY"]+height//2), 0)

        # draw close cross
        self.black_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        self.black_shader.bind()
        self.black_shader.uniform_float("color", (1,1,1,1))

        self.create_close_cross(context, close_button_size, padding+10, 4)
        bgl.glLineWidth(close_cross_width)
        self.close_cross_batch.draw(self.black_shader)