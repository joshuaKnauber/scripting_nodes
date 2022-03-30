import bpy
from ..base_node import SN_ScriptingBaseNode



class VariableReferenceNode():

    def on_var_changed(self): pass

    def var_update(self, context):
        self.on_var_changed()
        self._evaluate(context)
    
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Node Tree",
                                    description="Node Tree to get the variable from",
                                    update=var_update)

    var_name: bpy.props.StringProperty(name="Variable",
                                    description="Variable to get the value from",
                                    update=var_update)
    
    def on_var_change(self):
        pass
    
    def get_var(self):
        if self.ref_ntree and self.var_name in self.ref_ntree.variables:
            return self.ref_ntree.variables[self.var_name]
        return None
    
    def draw_variable_reference(self, layout):
        row = layout.row(align=True)
        row.prop(self, "ref_ntree", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.ref_ntree != None
        parent_tree = self.node_tree if not self.ref_ntree else self.ref_ntree
        subrow.prop_search(self, "var_name", parent_tree, "variables", text="")