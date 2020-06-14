import bpy

class SN_ProgramSocket(bpy.types.NodeSocket):
  bl_idname = "SN_ProgramSocket"
  bl_label = "Program Socket"

  def draw(self, context, layout, node, text):
    layout.label(text=text)

  def draw_color(self, context, node):
    return (1,1,1,1)