import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import blf
import bgl



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
        return {'CANCELLED'}

    def modal(self, context, event):
        # if context.area:
        #     context.area.tag_redraw()

        if event.type in ("RIGHTMOUSE", "ESC"):
            return self.close(context)

        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            m_x = event.mouse_region_x
            m_y = event.mouse_region_y
            for button in self.buttons:
                if m_x >= button["minX"] and m_x <= button["maxX"]:
                    if m_y >= button["minY"] and m_y <= button["maxY"]:

                        if button["url"]:
                            bpy.ops.wm.url_open(url=button["url"])
                        if button["callback"]:
                            button["callback"]()
                        if button["close"]:
                            return self.close(context)

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

    def draw_callback(self, context):
        self.buttons.clear()
        if context.space_data.tree_type == "ScriptingNodesTree":
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
            font_id = 0
            blf.position(font_id, padding+10, padding+10, 0)
            blf.size(font_id, 14, 72)
            blf.color(font_id, 1,1,1, 1.0)


            if self.show_node_info:
                node = context.space_data.node_tree.nodes.active
                blf.draw(font_id, "SERPENS - Node Info: "+node.bl_label)