#SN_ObjectDataNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ObjectDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectDataNode"
    bl_label = "Object Data"
    bl_icon = "OUTLINER_OB_GROUP_INSTANCE"
    node_color = (0.53, 0.55, 0.53)
    should_be_registered = False

    def get_data_type(self, context):
        items = []
        for dataType in bpy.data.rna_type.properties:
            if dataType.type == "COLLECTION":
                items.append((dataType.identifier, dataType.name, dataType.description))
        return sorted(items)

    def reset_data_type(self, context):
        if self.outputs[0].is_linked:
            if self.outputs[0].links[0].to_socket.bl_idname == "SN_CollectionSocket":
                self.outputs[0].links[0].to_node.reset_data_type(None)

    data_type_enum: bpy.props.EnumProperty(items=get_data_type, name="Data", description="The object data type", update=reset_data_type)

    def inititialize(self,context):
        self.sockets.create_output(self,"COLLECTION","Data block collection")

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type_enum", text="")

    def evaluate(self, socket, input_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["bpy.data." + self.data_type_enum]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": []
        }

    def data_type(self, output):
        bpy_type = str(eval("bpy.data.bl_rna.properties['" + self.data_type_enum + "'].fixed_type.identifier"))
        return "bpy.types." + bpy_type

    def required_imports(self):
        return ["bpy"]