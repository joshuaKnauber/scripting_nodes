import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_SetModalCursorNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_SetModalCursorNode"
    bl_label = "Set Modal Cursor"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        
    def cursor_items(self, context):
        items = []
        types = ['CROSSHAIR', 'DEFAULT', 'NONE', 'WAIT', 'MOVE_X', 'MOVE_Y', 'KNIFE', 'TEXT', 'PAINT_BRUSH', 'PAINT_CROSS', 'DOT', 'ERASER', 'HAND', 'SCROLL_X', 'SCROLL_Y', 'SCROLL_XY', 'EYEDROPPER', 'PICK_AREA', 'STOP', 'COPY', 'CROSS', 'MUTE', 'ZOOM_IN', 'ZOOM_OUT']
        for cursor in types:
            items.append((cursor, cursor.replace("_", " ").title(), cursor))
        return items

    cursor: bpy.props.EnumProperty(items=cursor_items,
                            name="Cursor",
                            description="The cursor to use while the modal is running",
                            update=SN_ScriptingBaseNode._evaluate)
        
    def draw_node(self, context, layout):
        layout.prop(self, "cursor")
    
    def evaluate(self, context):
        self.code = f"""
        context.window.cursor_set('{self.cursor}')
        {self.indent(self.outputs[0].python_value, 2)}
        """