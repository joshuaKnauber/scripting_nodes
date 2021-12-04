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
            self.code_register = f""
            # self.code_unregister = f""
        else:
            if self.icon_file:
                uid = self.uuid
                self.outputs["Icon"].python_value = f"bpy.context.scene.sn_icons_{uid}['{ self.icon_file.name.replace(' ', '_').upper() }'].icon_id"
                self.code_register = f"""
                        bpy.types.Scene.sn_icons_{uid} = {{}}
                        bpy.types.Scene.sn_icons_{uid}['{self.icon_file.name.replace(' ', '_').upper()}'] = bpy.data.images['{self.icon_file.name}'].preview
                        """
                self.code_unregister = f"del bpy.types.Scene.sn_icons_{uid}"
            else:
                self.outputs["Icon"].python_value = "0"
                self.code_register = ""
                self.code_unregister = ""


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
        row.scale_y = 1.2
        row.prop(self,"icon_source",expand=True)

        if self.icon_source == "BLENDER":
            op = layout.operator("sn.select_icon", text="Choose Icon", icon_value=self.icon)
            op.node = self.name
            op.socket = -1
        else:
            layout.template_ID(self, "icon_file", new="image.new", open="image.open", live_icon=True)

