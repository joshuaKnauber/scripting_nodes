import bpy
from ..use_operator import SN_UseOperatorNode
from ...compile.operators import SN_OT_EmptyOperator
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ...node_sockets import update_socket_autocompile


class SN_UiButtonNode(bpy.types.Node, SN_UseOperatorNode):
    '''Node for making a Button'''
    bl_idname = 'SN_UiButtonNode'
    bl_label = "Button"
    bl_icon = node_icons["INTERFACE"]

    buttonName: bpy.props.StringProperty(name="Name", description="The text displayed on the button")

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.outputs.new('SN_LayoutSocket', "Layout")

        self.generate_sockets()
        self.op_items()

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"buttonName")
        layout.prop_search(self,"opType",context.scene,"sn_op_type_properties",text="")
        layout.label(text=self.opDescription)

    def evaluate(self,output):
        opType = self.get_identifier().replace("bpy.ops.","")
        props = []

        for inp in self.inputs:
            if not inp.is_linked:
                value = inp.value
                if type(value) == str:
                    newProps = ["_INDENT__INDENT_operator.", inp.name.lower().replace(" ","_"), " = '", value, "'\n"]
                    props.append(newProps)
                elif inp.bl_idname == "SN_VectorSocket":
                    tuple_value = value
                    value = "("
                    for entry in tuple_value:
                        value += str(entry) + ","
                    value += ")"
                    newProps = ["_INDENT__INDENT_operator.", inp.name.lower().replace(" ","_"), " = ", value, "\n"]
                    props.append(newProps)
                else:
                    value = str(value)
                    newProps = ["_INDENT__INDENT_operator.", inp.name.lower().replace(" ","_"), " = ", value, "\n"]
                    props.append(newProps)
            else:
                newProps = ["_INDENT__INDENT_operator.", inp.name.lower().replace(" ","_"), " = ", inp.links[0].from_socket, "\n"]
                props.append(newProps)
        
        allProps = []
        for prop in props:
            allProps+=prop

        return {"code": ["_INDENT__INDENT_operator = ", self.outputs[0].links[0].to_node.layout_type(), ".operator('", opType, "', ", "text='", self.buttonName, "')\n"] + allProps}

