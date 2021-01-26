import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_AppendNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AppendNode"
    bl_label = "Append from File"
    # bl_icon = "GRAPH"
    bl_width_default = 250

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def get_append_types(self, context):
        items = ["Brush", "Camera", "Collection", "FreestyleLineStyle", "Image", "Light", "Material", "Mesh", "NodeTree", "Object", "Palette", "Scene", "Text", "Texture", "WorkSpace", "World"]

        tuple_items = []
        for item in items:
            tuple_items.append((item, item, ""))
        return tuple_items

    append_type: bpy.props.EnumProperty(items=get_append_types, name="Type", description="Type of the Append object", update=SN_ScriptingBaseNode.auto_compile)

    def on_create(self,context):
        self.add_execute_input("Append from File")
        self.add_execute_output("Execute").mirror_name = True

        self.add_string_input("Path").subtype = "FILE"
        self.add_string_input("Name")
        self.add_boolean_input("Linked")

    def draw_node(self, context, layout):
        layout.prop(self, "append_type")


    def code_evaluate(self, context, touched_socket):
        filepath=f'{self.inputs[1].code()} + r"\{self.append_type}"'

        return {
            "code": f"""
                    bpy.ops.wm.append(directory={filepath}, filename={self.inputs[2].code()}, link={self.inputs[3].code()})
                    {self.outputs[0].code(5)}
                    """
        }