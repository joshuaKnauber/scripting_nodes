import bpy


class ScriptingNodesAddonPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__.partition('.')[0]

    def _draw_install_package(self,layout):
        """ draws the button for installing packages """
        row = layout.row()
        row.scale_y = 1.5
        split = row.split(factor=0.5)
        split.operator("scripting_nodes.install_package",icon="PACKAGE")
        split.label(text="")

    def draw(self, context):
        layout = self.layout
        layout.label(text="Installed packages:")
        box = layout.box()
        column = box.column(align=True)
        column.label(text="Base Nodes")
        row = column.row()
        row.enabled = False
        row.label(text="The basic nodes to create addons")

        self._draw_install_package(layout)


"""
Access:
addon_prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
"""
