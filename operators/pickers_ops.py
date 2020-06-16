import bpy


class SN_OT_PanelPicker(bpy.types.Operator):
    bl_idname = "scripting_nodes.panel_picker"
    bl_label = "Panel Location Picker"
    bl_description = "Pick a space to place your panel in"
    bl_options = {'REGISTER',"UNDO","INTERNAL"}

    node_name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        context.window.cursor_set("EYEDROPPER")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def _set_panel_location(self,context,space_type,region_type):
        """ sets the panel location """
        node = context.space_data.node_tree.nodes[self.node_name]

    def _get_panel_location(self,context,event):
        """ returns the panel location """
        for area in context.screen.areas:
            if area.x < event.mouse_x < area.x + area.width and area.y < event.mouse_y < area.y + area.height:
                region_type = ["",999999,999999]
                for region in area.regions:
                    if region.x < event.mouse_x < region.x + region.width and region.y < event.mouse_y < region.y + region.height:
                        if region_type[1] > region.x + region.width - event.mouse_x:
                            if region_type[2] > region.y + region.height - event.mouse_y:
                                region_type[0] = region.type
                                region_type[1] = region.x + region.width - event.mouse_x
                                region_type[2] = region.y + region.height - event.mouse_y
                region_type = region_type[0]
                if region_type:
                    self._set_panel_location(context,area.type,region_type)

    def modal(self, context, event):
        context.window.cursor_set("EYEDROPPER")
        
        if event.type == "LEFTMOUSE":
            self._get_panel(context,event)
            context.window.cursor_set("DEFAULT")
            return {"FINISHED"}
        
        if event.type in {"RIGHTMOUSE", "ESC"}:
            return {"CANCELLED"}
        
        return {"PASS_THROUGH"}
