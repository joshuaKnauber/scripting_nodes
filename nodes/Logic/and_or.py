import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_AndOrNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AndOrNode"
    bl_label = "And/Or"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    operation: bpy.props.EnumProperty(items=[(" and ", "And", "Both values have to be true"), (" or ", "Or", "Only one value has to be true")], name="Gate", description="The gate you want to use", update=SN_ScriptingBaseNode.update_needs_compile)

    def on_create(self,context):
        self.add_boolean_input("Boolean")
        self.add_boolean_input("Boolean")
        self.add_dynamic_boolean_input("Boolean")
        self.add_boolean_output("Boolean")
    
    
    def draw_node(self, context, layout):
        layout.prop(self, "operation", expand=True)


    def code_evaluate(self, context, touched_socket):
        
        values = []
        for inp in self.inputs:
            if inp != self.inputs[-1]:
                if inp == self.inputs[-2]:
                    values.append(inp.value)
                else:
                    values.append(inp.value + self.operation)
                    
        return {
            "code": f"{self.list_values(values,0)}"
        }