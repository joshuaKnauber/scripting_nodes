import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_VariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for using and changing a variable'''
    bl_idname = 'SN_VariableNode'
    bl_label = "Variable"
    bl_icon = node_icons["OPERATOR"]

    def items_fetch(self, context):
        variable_nodes = []
        
        for node in context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_VariableSetNode":
                if node.name != "":
                    variable_nodes.append((str(node.name), str(node.name), ""))

        return variable_nodes

    name: bpy.props.EnumProperty(items=items_fetch, name="Name", description="Name of the variable", default=None, update=None, get=None, set=None)


    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        valueOut = self.outputs.new('SN_DataSocket', 'Data')


    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self, "name")

    def evaluate(self,output):
        return {"code": [self.name]}

