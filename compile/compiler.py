import bpy
from .compiler_data import gpl_block, addon_info

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

    def _only_string(self, value_list):
        for value in value_list:
            if not type(value) == str:
                return False
        return True

    def _compile_functions(self, tree):
        function_nodes = []
        functions = []
        
        for node in tree.nodes:
            if node.bl_idname == "SN_FunctionNode":
                function_nodes.append(node)

        for function_node in function_nodes:
            active_function_node = function_node
            function = ""

            while len(active_function_node.outputs["Program"].links) > 0:
                active_function_node = active_function_node.outputs["Program"].links[0].to_node

                line = active_function_node.evaluate(None)["code"]

                while not self._only_string(line):
                    for i, snippet in enumerate(line):
                        if not type(snippet) == str:
                            line.pop(i)
                            for subsnippet in snippet.node.evaluate(snippet)["code"]:
                                line.insert(i,subsnippet) 

                line = ("").join(line)
                function += line + "\n"

            functions.append(function)
        
        self._functions = functions

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

        text.write(gpl_block)
        text.write("\n")
        text.write(addon_info(tree))
        text.write("\n")
        
        for function in self._functions:
            text.write(function)
            text.write("\n")

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