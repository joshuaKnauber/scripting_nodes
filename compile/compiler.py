import bpy

class ScriptingNodesCompiler():

    def __init__(self):
        self.registered_functions = []
        self.registered_operators = []
        self.registered_panels = []

    def _is_scripting_tree(self):
        if bpy.context.space_data.tree_type == 'ScriptingNodesTree':
            return bpy.context.space_data.node_tree != None

    def _compile_operators(self, tree):
        operator_starts = []
        for node in tree.nodes:
            if node.bl_idname == "":
                operator_starts.append(node)

    def recompile(self):
        tree = bpy.context.space_data.node_tree
        if self._is_scripting_tree():

            function_starts = []
            
            self._compile_operators(tree)