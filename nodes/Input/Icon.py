import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IconNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IconNode"
    bl_label = "Icon"
    node_color = "ICON"
    bl_width_default = 200

    def on_create(self, context):
        inp = self.add_string_input("Image Path")
        inp.subtype = "FILE_PATH"
        inp.hide = True
        self.add_icon_output("Icon")
                
                
    def update_icon_source(self, context):
        if self.icon_source == "PATH":
            self.inputs[0].hide = False
        else:
            self.inputs[0].hide = True
        self._evaluate(context)

    icon_source: bpy.props.EnumProperty(name="Icon Source",
                                        description="The source of the icons",
                                        items=[("BLENDER","Blender","Blender",0),
                                                ("CUSTOM","Image","Image",1),
                                                ("PATH","Path","Path",2)],
                                        update=update_icon_source)


    icon: bpy.props.IntProperty(name="Value", description="Value of this socket", update=SN_ScriptingBaseNode._evaluate)

    def update_icon_file(self, context):
        if self.icon_file:
            self.icon_file.preview_ensure()
        self._evaluate(context)

    icon_file: bpy.props.PointerProperty(type=bpy.types.Image,
                                        name="Image File",
                                        description="The image you want to use as an icon",
                                        update=update_icon_file)


    def evaluate(self, context):
        if self.icon_source == "BLENDER":
            self.outputs["Icon"].python_value = f"{self.icon}"
        elif self.icon_source == "CUSTOM":
            if self.icon_file:
                self.outputs["Icon"].python_value = f"bpy.data.images['{self.icon_file.name}'].preview.icon_id"
            else:
                self.outputs["Icon"].python_value = "0"
        elif self.icon_source == "PATH":
            self.code_import = "import os"
            self.code_imperative = f"""
                                    def load_preview_icon(path):
                                        if os.path.exists(path):
                                            if not path in bpy.context.scene.sn_icons:
                                                bpy.context.scene.sn_icons.load(path, path, "IMAGE")
                                            return bpy.context.scene.sn_icons[path].icon_id
                                        return 0
                                    """
            self.outputs["Icon"].python_value = f"load_preview_icon({self.inputs[0].python_value})"
    
    
    def evaluate_export(self, context):
        # maybe dont save in property, use global dict or something similar instead
        # TODO
        if self.icon_source == "BLENDER":
            self.outputs["Icon"].python_value = f"{self.icon}"
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


    def draw_node(self, context, layout):
        row = layout.row()
        row.scale_y = 1.2
        row.prop(self,"icon_source",expand=True)

        if self.icon_source == "BLENDER":
            op = layout.operator("sn.select_icon", text="Choose Icon", icon_value=self.icon)
            op.icon_data_path = f"bpy.data.node_groups['{self.node_tree.name}'].nodes['{self.name}']"
        elif self.icon_source == "CUSTOM":
            layout.template_ID(self, "icon_file", new="image.new", open="image.open", live_icon=True)
            if self.icon_file and not self.icon_file.filepath:
                layout.label(text="Image not saved!", icon="ERROR")