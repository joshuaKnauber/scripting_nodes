import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ListBlendContentNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ListBlendContentNode"
    bl_label = "List Blend File Content"

    def on_create(self, context):
        self.add_string_input("Path").subtype = "FILE_PATH"
        self.add_list_output("Names")

    def get_append_types(self, context):
        items = ["actions", "armatures", "bruhes", "cache_files", "cameras", "collections", "curves",
                "images", "fonts", "grease_pencils", "lattices", "libraries", "lightprobes", "lights",
                "linestyles", "masks", "materials", "meshes", "metaballs", "movieclips", "node_groups",
                "objects", "paint_curves", "palettes", "particles", "pointclouds", "scenes",  "screens",
                "shape_keys", "sounds", "speakers", "texts", "textures", "volumes", "workspaces", "worlds"]

        tuple_items = []
        for item in items:
            tuple_items.append((item, item.replace("_", " ").title(), item))
        return tuple_items

    append_type: bpy.props.EnumProperty(items=get_append_types, name="Type", description="Type of the Append object", update=SN_ScriptingBaseNode._evaluate)

    def draw_node(self, context, layout):
        layout.prop(self, "append_type")
        
    def evaluate(self, context):
        self.code_imperative = """
        def get_blend_contents(path, data_type):
            if os.path.exists(path):
                with bpy.data.libraries.load(path) as (data_from, data_to):
                    return getattr(data_from, data_type)
            return []
        """
        self.code_import = "import os"
        self.outputs[0].python_value = f"get_blend_contents({self.inputs[0].python_value}, '{self.append_type}')"