import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import blf
import bgl
import requests


class SN_DrawMarketplace(bpy.types.Operator):
    bl_idname = "scripting_nodes.draw_marketplace"
    bl_label = "Draw Marketplace"
    bl_description = "Draws the marketplace"
    bl_options = {"REGISTER"}

    package_index: bpy.props.IntProperty(default=0,options={"SKIP_SAVE"})

    def invoke(self, context, event):
        url = "https://raw.githubusercontent.com/joshuaKnauber/visual_scripting_addon_docs/packages/packages.json"
        try:
            self.packages = requests.get(url).json()["packages"]

            self.buttons = []
            self.handler = bpy.types.SpaceNodeEditor.draw_handler_add(self.draw_callback,(context,),'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            context.area.tag_redraw()
            return {"RUNNING_MODAL"}

        except ValueError:
            self.report({"ERROR"},message="Couldn't find what we were looking for. Check your connection!")
            return {"FINISHED"}
        

    def close(self, context):
        bpy.types.SpaceNodeEditor.draw_handler_remove(self.handler, 'WINDOW')
        context.area.tag_redraw()
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == "ESC" or not context.scene.sn_properties.show_marketplace:
            context.scene.sn_properties.show_marketplace = False
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
                            context.scene.sn_properties.show_marketplace = False

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

    def create_background(self, context):
        width, height = self.get_width_height(context)
        
        vertices = (
            (0, 0), (0, height),
            (width, height), (width, 0),
        )
        indices = (
            (0, 1, 2), (0, 3, 2),
        )

        self.background_batch = batch_for_shader(self.black_shader, 'TRIS', {"pos": vertices}, indices=indices)

    def create_backdrop(self, context, box_width, box_height):
        width, height = self.get_width_height(context)
        
        x = width/2 - box_width/2
        y = height - box_height - 100
        vertices = (
            (x, y), (x, y+box_height),
            (x+box_width, y+box_height), (x+box_width, y),
        )
        indices = (
            (0, 1, 2), (0, 3, 2),
        )

        self.backdrop_batch = batch_for_shader(self.white_shader, 'TRIS', {"pos": vertices}, indices=indices)
        return x, y+box_height

    def create_box(self, context, shader, x, y, box_width, box_height):
        vertices = (
            (x, y), (x, y+box_height),
            (x+box_width, y+box_height), (x+box_width, y),
        )
        indices = (
            (0, 1, 2), (0, 3, 2),
        )

        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
        return batch, vertices

    def create_triangle(self, context, shader, x, y, box_width, box_height):
        vertices = (
            (x-box_width/2, y-box_height/2), (x-box_width/2, y+box_height/2),(x+box_width/2, y),
        )

        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices})
        return batch, vertices

    def create_close_button(self, context, size, padding):
        width, height = self.get_width_height(context)

        vertices = (
            (width-size-padding, height-padding), (width-padding, height-padding),
            (width-padding, height-size-padding), (width-size-padding, height-size-padding),
        )
        indices = (
            (0, 1, 2), (0, 3, 2)
        )

        self.close_batch = batch_for_shader(self.black_shader, 'TRIS', {"pos": vertices}, indices=indices)

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

        self.close_cross_batch = batch_for_shader(self.white_shader, 'LINES', {"pos": tuple(vertices)}, indices=tuple(indices))

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


    def draw_package(self,package,x,y,scale):
        # draw title
        self.draw_text("["+package["title"]+"](0,0,0)",int(16*scale),(x,y),0)
        y -= 25*scale

        # draw price
        self.draw_text("["+package["price"]+"](0.1,1,0.2)",int(14*scale),(x,y),0)
        y -= 25*scale

        # draw text
        for index, line in enumerate(package["text"]):
            y -= 20*scale
            self.draw_text("["+line+"](0,0,0)",int(13*scale),(x,y),0)

        # draw button
        blf.size(0, int(14*scale), 72)
        btn_width, btn_height = blf.dimensions(0, "Get it!")
        x_padding = 40*scale
        y_padding = 10*scale

        y -= 25*scale
        vertices = ((x, y+y_padding), (x+btn_width+x_padding*2, y+y_padding),
                    (x+btn_width+x_padding*2, y-btn_height-y_padding), (x, y-btn_height-y_padding))
        indices = ((0, 1, 2), (0, 3, 2))

        self.get_btn_batch = batch_for_shader(self.blue_shader, 'TRIS', {"pos": vertices}, indices=indices)

        self.get_btn_batch.draw(self.blue_shader)
        self.buttons.append({
            "minX": min(vertices, key = lambda t: t[0])[0],
            "minY": min(vertices, key = lambda t: t[1])[1],
            "maxX": max(vertices, key = lambda t: t[0])[0],
            "maxY": max(vertices, key = lambda t: t[1])[1],
            "close": False,
            "url": package["url"],
            "callback": None
        })

        self.draw_text("Get it!",int(14*scale),(x+x_padding,y-btn_height),0)


    def prev_package(self):
        if self.package_index != 0:
            self.package_index -= 1
        else:
            self.package_index = len(self.packages)-1

    def next_package(self):
        if self.package_index < len(self.packages)-1:
            self.package_index += 1
        else:
            self.package_index = 0


    def draw_callback(self, context):
        self.buttons = []
        if context.space_data.tree_type == "ScriptingNodesTree":
            scale = context.scene.sn_properties.tutorial_scale
            width, height = self.get_width_height(context)
            outline_width = 1.5 * scale
            close_button_size = 20 * scale
            close_cross_width = 5 * scale
            font_size_title = int(14 * scale)
            font_size_text = int(13 * scale)

            # draw background
            self.black_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            self.black_shader.bind()
            self.black_shader.uniform_float("color", (0.1, 0.1, 0.1, 1.0))

            self.create_background(context)
            self.background_batch.draw(self.black_shader)

            # draw close button
            vertices = self.create_close_button(context, close_button_size, 0)
            self.close_batch.draw(self.black_shader)
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
            self.white_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            self.white_shader.bind()
            self.white_shader.uniform_float("color", (1, 1, 1, 1.0))

            self.create_close_cross(context, close_button_size, 0, 4)
            bgl.glLineWidth(close_cross_width)
            self.close_cross_batch.draw(self.white_shader)

            # package backdrop
            backdrop_width = 400
            backdrop_height = 500
            x,y = self.create_backdrop(context,backdrop_width*scale, backdrop_height*scale)
            self.backdrop_batch.draw(self.white_shader)
        
            # draw packages
            self.blue_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            self.blue_shader.bind()
            self.blue_shader.uniform_float("color", (0.2, 0.1, 1, 1.0))

            self.draw_package(self.packages[self.package_index],x + 30*scale,y-40*scale,scale)

            # draw package buttons
            self.grey_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            self.grey_shader.bind()
            self.grey_shader.uniform_float("color", (0.15, 0.15, 0.15, 1.0))

            z_factor = 0.8

            button_verts = []
            batch, vertices = self.create_box(context, self.grey_shader, width/2+100*scale, height-100, backdrop_width*scale*z_factor, 50*scale*z_factor)
            batch.draw(self.grey_shader)
            button_verts.append((vertices,self.next_package))

            batch, vertices = self.create_box(context, self.grey_shader, width/2-100*scale, height-100, -backdrop_width*scale*z_factor, 50*scale*z_factor)
            batch.draw(self.grey_shader)
            button_verts.append((vertices,self.prev_package))

            batch, vertices = self.create_box(context, self.grey_shader, width/2+200*scale, height - 100 - backdrop_height*scale + 50*scale*(1+z_factor), backdrop_width*scale*z_factor-100*scale, backdrop_height*scale*z_factor + 50*scale*z_factor)
            batch.draw(self.grey_shader)
            button_verts.append((vertices,self.next_package))

            batch, vertices = self.create_box(context, self.grey_shader, width/2-200*scale, height - 100 - backdrop_height*scale + 50*scale*(1+z_factor), -(backdrop_width*scale*z_factor-100*scale), backdrop_height*scale*z_factor + 50*scale*z_factor)
            batch.draw(self.grey_shader)
            button_verts.append((vertices,self.prev_package))

            for vertices in button_verts:
                self.buttons.append({
                    "minX": min(vertices[0], key = lambda t: t[0])[0],
                    "minY": min(vertices[0], key = lambda t: t[1])[1],
                    "maxX": max(vertices[0], key = lambda t: t[0])[0],
                    "maxY": max(vertices[0], key = lambda t: t[1])[1],
                    "close": False,
                    "url": None,
                    "callback": vertices[1]
                })

            self.light_grey_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            self.light_grey_shader.bind()
            self.light_grey_shader.uniform_float("color", (0.22, 0.22, 0.22, 1.0))

            batch, vertices = self.create_triangle(context, self.light_grey_shader, width/2+backdrop_width/2*scale*z_factor+100*scale, height - 100 - backdrop_height/2*scale + 50*scale*(z_factor)+25*scale*z_factor, 40*scale, 80*scale)
            batch.draw(self.light_grey_shader)
            
            batch, vertices = self.create_triangle(context, self.light_grey_shader, width/2-backdrop_width/2*scale*z_factor-100*scale, height - 100 - backdrop_height/2*scale + 50*scale*(z_factor)+25*scale*z_factor, -40*scale, 80*scale)
            batch.draw(self.light_grey_shader)