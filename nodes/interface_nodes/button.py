import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ...node_sockets import update_socket_autocompile


class SN_UiButtonNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for making a Button'''
    bl_idname = 'SN_UiButtonNode'
    bl_label = "Button"
    bl_icon = node_icons["INTERFACE"]

    def items_fetch(self, context):
        operator_nodes = []
        
        for node in context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_OperatorNode":
                operator_nodes.append((str(node.operator_name), str(node.operator_name), ""))

        return operator_nodes

    operatorName: bpy.props.EnumProperty(items=items_fetch, name="Operator", description="Operator Name", default=None, update=update_socket_autocompile, get=None, set=None)


    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.outputs.new('SN_LayoutSocket', "Layout")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"operatorName")

    def evaluate(self,output):
        idname_lower = self.operatorName.lower().replace(" ","_")
        return {"code": ["_INDENT__INDENT_", self.outputs[0].links[0].to_node.layout_type(), ".operator('sn.", idname_lower, "')\n"]}