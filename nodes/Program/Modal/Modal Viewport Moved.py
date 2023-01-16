import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ModalViewportMovedNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ModalViewportMovedNode"
    bl_label = "Modal Viewport Moved"
    node_color = "DEFAULT"

    def on_create(self, context):
        self.add_boolean_output("Viewport Moved")

    def evaluate(self, context):
        self.code_imperative = """
        def is_event_view_move(event):
            view2d_ops = ["view2d.pan", "view2d.scroll_right", "view2d.scroll_left", "view2d.scroll_down",
                        "view2d.scroll_up", "view2d.ndof", "view2d.ndof", "view2d.ndof", "view2d.zoom_out",
                        "view2d.zoom_in", "view2d.zoom", "view2d.zoom_border"]
            
            view3d_ops = ["view3d.move", "view3d.zoom", "view3d.dolly", "view3d.view_selected", "view3d.smoothview",
                        "view3d.view_all", "view3d.view_axis", "view3d.view_persportho", "view3d.view_orbit",
                        "view3d.view_center_pick", "view3d.ndof_orbit_zoom", "view3d.ndof_orbit", "view3d.ndof_pan",
                        "view3d.ndof_all", "view3d.view_roll", "view3d.zoom_border"]
            
            items_2d = bpy.context.window_manager.keyconfigs[bpy.context.preferences.keymap.active_keyconfig].keymaps['View2D'].keymap_items
            for item in items_2d:
                if item.idname in view2d_ops:
                    if event.type == item.type and event.shift == bool(item.shift) and event.alt == bool(item.alt) and event.ctrl == bool(item.ctrl) and event.oskey == bool(item.oskey):
                        return True

            items_3d = bpy.context.window_manager.keyconfigs[bpy.context.preferences.keymap.active_keyconfig].keymaps['3D View'].keymap_items
            for item in items_3d:
                if item.idname in view3d_ops:
                    if event.type == item.type and event.shift == bool(item.shift) and event.alt == bool(item.alt) and event.ctrl == bool(item.ctrl) and event.oskey == bool(item.oskey):
                        return True
                
            return False
        """
        
        self.outputs[0].python_value = f"is_event_view_move(event)"