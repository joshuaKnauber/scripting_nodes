import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_AppendFromFileNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AppendFromFileNode"
    bl_label = "Append From File"
    bl_width_default = 200
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()

        self.add_string_input("Path").subtype = "FILE_PATH"
        self.add_string_input("Name")
        self.add_boolean_input("Linked")
        self.add_property_output("Appended")
        
    append_names = ["Action", "Brush", "Camera", "Collection", "FreestyleLineStyle", "Image", "Light", "Material",
                "Mesh", "NodeTree", "Object", "Palette", "Scene", "Text", "Texture", "WorkSpace", "World"]
    data_names = ["actions", "brushes", "cameras", "collections", "linestyles", "images", "lights", "materials",
                "meshes", "node_groups", "objects", "palettes", "scenes", "texts", "textures", "workspaces", "worlds"]

    def get_append_types(self, context):
        items = self.append_names
        tuple_items = []
        for item in items:
            tuple_items.append((item, item.replace("_", " ").title(), item))
        return tuple_items

    append_type: bpy.props.EnumProperty(items=get_append_types, name="Type", description="Type of the Append object", update=SN_ScriptingBaseNode._evaluate)

    def draw_node(self, context, layout):
        layout.prop(self, "append_type")

    def evaluate(self, context):
        filepath=f"{self.inputs[1].python_value} + r'\{self.append_type}'"

        data_name = self.data_names[self.append_names.index(self.append_type)]
        self.code = f"""
                    before_data = list(bpy.data.{data_name})
                    bpy.ops.wm.append(directory={filepath}, filename={self.inputs[2].python_value}, link={self.inputs[3].python_value})
                    new_data = list(filter(lambda d: not d in before_data, list(bpy.data.{data_name})))
                    appended_{self.static_uid} = None if not new_data else new_data[0]
                    {self.indent(self.outputs[0].python_value, 5)}
                    """
                    
        if "Appended" in self.outputs:
            self.outputs["Appended"].python_value = f"appended_{self.static_uid}"