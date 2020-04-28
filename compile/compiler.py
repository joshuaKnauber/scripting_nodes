import bpy

class ScriptingNodesCompiler():

    def __init__(self):
        self._registered_functions = []
        self._registered_operators = []
        self._registered_panels = []

    def _is_scripting_tree(self):
        if bpy.context.space_data.tree_type == 'ScriptingNodesTree':
            return bpy.context.space_data.node_tree != None

    def _compile_operators(self, tree):
        operator_starts = []
        for node in tree.nodes:
            if node.bl_idname == "":
                operator_starts.append(node)

    def _reset(self):
        self._registered_functions = []
        self._registered_operators = []
        self._registered_panels = []

    def recompile(self):
        tree = bpy.context.space_data.node_tree
        if self._is_scripting_tree():

            self._reset()

            function_starts = []
            
            self._compile_operators(tree)