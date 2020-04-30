import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_VariableChangeNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for changing a variable'''
    bl_idname = 'SN_VariableChangeNode'
    bl_label = "Change Variable"
    bl_icon = node_icons["OPERATOR"]

    def allNodes(self, context):
        all_nodes = []
        for inNodes in self.inputs[0].links[0].from_node:
            pass
        return all_nodes

    def items_fetch(self, context):
        variable_nodes = allNodes(context)

        print(self.inputs[0].links[0].from_node)
        
        for node in context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_VariableSetNode":
                if node.name != "":
                    variable_nodes.append((str(node.name), str(node.name), ""))

        return variable_nodes

    name: bpy.props.EnumProperty(items=items_fetch, name="Name", description="Name of the variable", default=None, update=None, get=None, set=None)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        pIn = self.inputs.new('SN_ProgramSocket', "Program")
        pIn.display_shape = "DIAMOND"

        value = self.inputs.new('SN_DataSocket', 'Value')

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self, "name")

    def evaluate(self,output):
        errors = []
        if not self.inputs[1].is_linked:
            errors.append("no_connection")
            return {"code": [self.name, " = ", "0", "\n"], "error": errors}
        else:
            return {"code": [self.name, " = ", self.inputs[1].links[0].from_socket, "\n"]}
