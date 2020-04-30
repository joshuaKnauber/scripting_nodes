import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ...node_sockets import update_socket_autocompile


class SN_VariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for using and changing a variable'''
    bl_idname = 'SN_VariableNode'
    bl_label = "Variable"
    bl_icon = node_icons["OPERATOR"]

    def connected_nodes(self, node):
        nodes = []
        for inp in node.inputs:
            if inp.is_linked:
                nodes.append(inp.links[0].from_node)
        for out in node.outputs:
            if out.is_linked:
                nodes.append(out.links[0].to_node)
        return nodes

    def items_fetch(self, context):
        all_nodes = [self]

        found_new_node = True
        while found_new_node:
            found_new_node = False
            for node in all_nodes:
                for connected in self.connected_nodes(node):
                    if not connected in all_nodes:
                        all_nodes.append(connected)
                        found_new_node = True
        
        variable_nodes = []
        for node in all_nodes:
            if node.bl_idname == "SN_VariableSetNode":
                if node.variable_name != "":
                    variable_nodes.append((str(node.variable_name), str(node.variable_name), ""))

        return variable_nodes

    
    variable_name: bpy.props.EnumProperty(items=items_fetch, name="Name", description="Name of the variable", default=None, update=update_socket_autocompile, get=None, set=None)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        valueOut = self.outputs.new('SN_DataSocket', 'Data')


    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self, "variable_name")

    def evaluate(self,output):
        error = []

        if self.variable_name == "":
            error.append("no_available")

        return {"code": [self.variable_name], "error": error}
