import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_DataToIconNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DataToIconNode"
    bl_label = "Data To Icon"

    def on_create(self, context):
        self.add_string_input("Name")
        self.add_icon_output("Icon")
        
    data_type: bpy.props.EnumProperty(name="Type",
                                description="Type of data to preview",
                                items=[("bpy.data.materials", "Material", "Material"),
                                       ("bpy.data.objects", "Object", "Object"),
                                       ("bpy.data.images", "Image", "Image"),
                                       ("bpy.data.textures", "Texture", "Texture")],
                                update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        self.code_imperative = f"""
                                def get_id_preview_id(data):
                                    if hasattr(data, "preview"):
                                        if not data.preview:
                                            data.preview_ensure()
                                        if hasattr(data.preview, "icon_id"):
                                            return data.preview.icon_id
                                    return 0
                                """
        self.outputs["Icon"].python_value = f"get_id_preview_id({self.data_type}[{self.inputs['Name'].python_value}])"

    def draw_node(self, context, layout):
        layout.label(text="Use this node with care! This might slow down your UI", icon="INFO")
        layout.prop(self, "data_type")