import bpy

from ..base_socket import ScriptingSocket


class SNA_ProgramSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_ProgramSocket"
    bl_label = "Program"
    is_program = True

    def on_create(self, context: bpy.types.Context):
        self.display_shape = "DIAMOND"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        for inp in self.node.inputs:
            if getattr(inp, "is_program", False):
                next = inp.get_next()
                if next:
                    return next[0].get_color(context, next[0].node)
        return (0.2, 0.2, 0.2, 1)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
