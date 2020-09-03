import bpy
from .drawing_ops import DrawingFuncs


class SN_DrawDocs(DrawingFuncs, bpy.types.Operator):
    bl_idname = "scripting_nodes.draw_docs"
    bl_label = "Draw Docs"
    bl_description = "Draws the docs"
    bl_options = {"REGISTER","INTERNAL"}

    def close(self, context):
        bpy.types.SpaceNodeEditor.draw_handler_remove(self.handler, 'WINDOW')
        if context.area:
            context.area.tag_redraw()
        return {'FINISHED'}

    def modal(self, context, event):
        if not context.area or not context.area.type == "NODE_EDITOR":
            context.scene.sn_properties.show_node_info = False
            return self.close(context)
        elif context.area.type == "NODE_EDITOR" and not context.space_data.tree_type == "ScriptingNodesTree":
            context.scene.sn_properties.show_node_info = False
            return self.close(context)

        if event.type == "ESC" or not context.scene.sn_properties.show_node_info:
            context.scene.sn_properties.show_node_info = False
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
                            context.scene.sn_properties.show_node_info = False

        return {'PASS_THROUGH'}

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
            node = context.space_data.node_tree.nodes.active
            if node:
                if hasattr(node,"docs"):
                    self.draw_text("<serpens>SERPENS</> - Node Info: "+node.bl_label,font_size_title,(padding+10,padding+10),0)

                    # draw tutorial text
                    y_offset = height - padding - font_size_text - 10
                    for index, line in enumerate(node.docs["text"]):
                        y_offset -= index*2
                        if not line:
                            y_offset -= font_size_text
                        y_offset -= self.draw_text(line,font_size_text,(padding+10, y_offset),0)

                    # draw python text
                    if node.docs["python"] and context.scene.sn_properties.show_python_docs:
                        y_offset -= 40
                        y_offset -= self.draw_text("Python Example:",font_size_python,(padding+10,y_offset),0)
                        y_offset -= 8
                        for index, line in enumerate(node.docs["python"]):
                            y_offset -= index*4
                            y_offset -= self.draw_text(line,font_size_python,(padding+10, y_offset),0)
                else:
                    self.draw_text("<serpens>SERPENS</> - Select a node from the addon to show infos",font_size_title,(padding+10,padding+10),0)
            else:
                self.draw_text("<serpens>SERPENS</> - Select a node to show infos",font_size_title,(padding+10,padding+10),0)