import bpy


class WM_MT_button_context(bpy.types.Menu):
    bl_label = ""

    def draw(self, context):
        pass


def serpens_right_click(self, context: bpy.types.Context):
    layout = self.layout

    property_pointer = getattr(context, "button_pointer", None)
    property_value = getattr(context, "button_prop", None)
    button_value = getattr(context, "button_operator", None)

    layout.operator("sna.scrape", text="Scrape With Context")
