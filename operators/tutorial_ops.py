import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import blf
import bgl
import re



class SN_DrawTutorialFrame(bpy.types.Operator):
    bl_idname = "scripting_nodes.draw_tutorial"
    bl_label = "Draw Tutorial"
    bl_description = "Draws the tutorial"
    bl_options = {"REGISTER","INTERNAL"}

    show_node_info: bpy.props.BoolProperty(default=False,options={"SKIP_SAVE"})

    def invoke(self, context, event):
        self.buttons = []
        self.handler = bpy.types.SpaceNodeEditor.draw_handler_add(self.draw_callback,(context,),'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def close(self, context):
        bpy.types.SpaceNodeEditor.draw_handler_remove(self.handler, 'WINDOW')
        context.area.tag_redraw()
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == "ESC" or not context.scene.sn_properties.show_node_info:
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
                        context.scene.sn_properties.show_node_info = not button["close"]

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

        self.outline_batch = batch_for_shader(self.white_shader, 'LINES', {"pos": tuple(vertices)}, indices=tuple(indices))

    def create_close_button(self, context, size, padding):
        width, height = self.get_width_height(context)

        vertices = (
            (width-size-padding, height-padding), (width-padding, height-padding),
            (width-padding, height-size-padding), (width-size-padding, height-size-padding),
        )
        indices = (
            (0, 1, 2), (0, 3, 2)
        )

        self.close_batch = batch_for_shader(self.white_shader, 'TRIS', {"pos": tuple(vertices)}, indices=indices)

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
        split_text = text.split("[")
        
        for index, part in enumerate(split_text):

            is_valid = False
            if len(part.split("](")) > 1:
                colored_text = part.split("](")[0]
                part = ("](").join(part.split("](")[1:])
                if len(part.split(")")) > 1:
                    color = part.split(")")[0]
                    if len(color.split(",")) == 3 and color.replace(",","").replace(".","").replace(" ","").isdigit():
                        white_text = (")").join(part.split(")")[1:])
                        is_valid = True
            if not is_valid:
                if not index == 0:
                    part = "["+part
                processed.append( (part, (1,1,1,1)) )
            else:
                real_color = ( float(color.split(",")[0]), float(color.split(",")[1]), float(color.split(",")[2]), 1 )
                processed.append( (colored_text, real_color) )
                processed.append( (white_text, (1,1,1,1)) )

        return processed


    def syntax_highlight_text(self,text):
        processed = []
        
        return processed


    def draw_text(self,text,font_size,position,font_id,syntax_highlighting=False):
        if not syntax_highlighting:
            processed = self.process_text(text)
        else:
            processed = self.syntax_highlight_text(text)
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


    def draw_callback(self, context):
        self.buttons.clear()
        if context.space_data.tree_type == "ScriptingNodesTree":
            width, height = self.get_width_height(context)
            padding = 2
            outline_width = 1.5
            close_button_size = 20
            close_cross_width = 5

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
            if self.show_node_info:
                node = context.space_data.node_tree.nodes.active
                if node:
                    self.draw_text("SERPENS - Node Info: "+node.bl_label,14,(padding+10,padding+10),0)

                    # draw tutorial text
                    y_offset = height - padding - 20
                    for index, line in enumerate(node.docs["text"]):
                        y_offset -= index*5
                        y_offset -= self.draw_text(line,13,(padding+10, y_offset),0)

                    # draw python text
                    if node.docs["python"]:
                        y_offset -= 50
                        y_offset -= self.draw_text("PYTHON:",12,(padding+10,y_offset),0)
                        y_offset -= 10
                        for index, line in enumerate(node.docs["python"]):
                            y_offset -= index*5
                            y_offset -= self.draw_text(line,12,(padding+10, y_offset),0,True)
                else:
                    self.draw_text("SERPENS - Select a node to show infos",14,(padding+10,padding+10),0)