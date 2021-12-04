import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IconNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IconNode"
    bl_label = "Icon"
    node_color = "ICON"

    def on_create(self, context):
        self.add_icon_output("Icon")

    def evaluate(self, context):
        if self.icon_source == "BLENDER":
            self.outputs["Icon"].python_value = f"{self.icon}"
        else:
            self.outputs["Icon"].python_value = f"0"
            print(self.icon_file)
            self.register = f"""
                    bpy.types.Scene.sn_icons_{self.uid} = bpy.utils.previews.new()
                    import os
                    icons_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
                    # bpy.types.Scene.sn_icons_{self.uid}.load()
                    """


    icon_source: bpy.props.EnumProperty(name="Icon Source",
                                        description="The source of the icons",
                                        items=[("BLENDER","Blender","Blender",0),
                                                ("CUSTOM","Custom","Custom",1)],
                                        update=SN_ScriptingBaseNode._evaluate)

    icon: bpy.props.IntProperty(name="Value", description="Value of this socket", update=SN_ScriptingBaseNode._evaluate)

    icon_file: bpy.props.PointerProperty(type=bpy.types.Image,
                                        name="Image File",
                                        description="The image you want to use as an icon",
                                        update=SN_ScriptingBaseNode._evaluate)

    def draw_node(self, context, layout):
        row = layout.row()
        row.scale_y = 1.3
        row.prop(self,"icon_source",expand=True)

        if self.icon_source == "BLENDER":
            op = layout.operator("sn.select_icon", text="Choose Icon", icon_value=self.icon)
            op.node = self.name
            op.socket = -1
        else:
            col = layout.column()
            col.scale_y = 1.3
            col.template_ID(self, "icon_file", new="image.new", open="image.open", live_icon=True)

