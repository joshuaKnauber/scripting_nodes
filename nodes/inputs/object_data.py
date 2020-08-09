#SN_ObjectDataNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ObjectDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectDataNode"
    bl_label = "Object Data"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.53, 0.55, 0.53)
    should_be_registered = False

    def get_data_type(self, context):
        items = []
        for dataType in bpy.data.rna_type.properties:
            if dataType.type == "COLLECTION":
                items.append((dataType.identifier,dataType.name,dataType.description))
        return sorted(items)

    data_type_enum: bpy.props.EnumProperty(items=get_data_type, name="Data", description="The object data type")

    def inititialize(self,context):
        self.sockets.create_output(self,"COLLECTION","Object Collection")

    def draw_buttons(self, context, layout):
        layout.prop(self, "data_type_enum", text="")

    def evaluate(self, socket, input_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": []
        }
