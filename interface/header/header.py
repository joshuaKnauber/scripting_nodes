import bpy


def prepend_header(self, context):
    layout = self.layout


def append_header(self, context):
    layout = self.layout

    layout.prop(context.scene.sn,"editing_addon")