import bpy

class ScriptingNodesCompiler():

    def __init__(self):
        self._functions = []
        self._operators = []
        self._panels = []

    def _is_scripting_tree(self):
        if bpy.context.space_data.tree_type == 'ScriptingNodesTree':
            return bpy.context.space_data.node_tree != None

    def _reset(self):
        pass

    def _compile_functions(self, tree):
        pass

    def _compile_operators(self, tree):
        operator_starts = []
        for node in tree.nodes:
            if node.bl_idname == "":
                operator_starts.append(node)

    def _compile_interface(self, tree):
        pass

    def _create_file(self, tree):
        name = tree.addon_name.lower().replace(" ","_") + ".py"

        if not name in bpy.data.texts:
            bpy.data.texts.new(name=name)
        text = bpy.data.texts[name]

        text.clear()

        text.write("print('test')")

        return text

    def _register_file(self, addon):
        pass

    def recompile(self):
        tree = bpy.context.space_data.node_tree
        if self._is_scripting_tree():

            self._reset()

            self._compile_functions(tree)
            
            self._compile_operators(tree)

            self._compile_interface(tree)

            addon = self._create_file(tree)

            self._register_file(addon)