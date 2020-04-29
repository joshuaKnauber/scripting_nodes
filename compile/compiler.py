import bpy
from .compiler_data import gpl_block, addon_info, error_logs
from ..properties.property_utils import clear_error_props, add_error_prop, sn_props

class ScriptingNodesCompiler():

    def __init__(self):
        self._indents = 4
        self._errors = []
        self._functions = []
        self._operators = []
        self._panels = []

    def _is_scripting_tree(self):
        if bpy.context.space_data.tree_type == 'ScriptingNodesTree':
            return bpy.context.space_data.node_tree != None

    def _reset(self):
        clear_error_props()
        self._errors.clear()
        self._functions.clear()

    def _only_string(self, value_list):
        for value in value_list:
            if not type(value) == str:
                return False
        return True

    def _compile_script_line(self, line):
        while not self._only_string(line):
            for i, snippet in enumerate(line):
                if not type(snippet) == str:
                    line.pop(i)
                    line_part1 = line[:i]
                    line_part2 = line[i:]
                    function_value = snippet.node.evaluate(snippet)
                    if "error" in function_value:
                        for error in function_value["error"]:
                            self._errors.append([error,snippet.node])
                    line = line_part1 + function_value["code"] + line_part2
                    break
        return line

    def _compile_tree_branch(self, function_node, indents, evaluate_start_node, only_evaluate_start_node):
        code_blocks = ""
        continue_program = True

        while continue_program > 0 and not only_evaluate_start_node or evaluate_start_node:

            #get the next connected node if it's not the start node
            if len(function_node.outputs) > 0:
                if len(function_node.outputs[0].links) > 0 and not evaluate_start_node:
                    function_node = function_node.outputs[0].links[0].to_node

            #get the values from the function node
            function_value = function_node.evaluate(None)
            code_block = function_value["code"]

            #handle errors in the function node
            if "error" in function_value:
                for error in function_value["error"]:
                    self._errors.append([error,function_node])

            #add function nodes code to the entire code
            code_block = self._compile_script_line(code_block)
            if len(code_block) > 0:
                code_blocks += " "*indents + ("").join(code_block)

            #get the code for all the indented code blocks
            if "indented_blocks" in function_value:
                for block in function_value["indented_blocks"]:
                    #add the indented blocks code to the entire code
                    code_block = self._compile_script_line(block["code"])
                    if len(code_block) > 0:
                        code_blocks += " "*indents + ("").join(code_block)

                    #compile the connected tree and add it to the entire code
                    if block["function_node"]:
                        code_block = self._compile_tree_branch(block["function_node"],indents+self._indents, True, False)
                    else:
                        self._errors.append(["no_connection",function_node])
                        code_block = " "*(indents+self._indents) + "pass\n"
                    code_blocks += code_block

            #check if the program branch reached the end
            continue_program = False
            if len(function_node.outputs) > 0:
                if len(function_node.outputs[0].links) > 0:
                    continue_program = True

            evaluate_start_node = False
        
        return code_blocks

    def _compile_functions(self, tree):
        function_nodes = []
        
        for node in tree.nodes:
            if node.bl_idname == "SN_FunctionNode":
                function_nodes.append(node)

        for function_node in function_nodes:
            function = self._compile_tree_branch(function_node,0,True,True)
            self._functions.append(function)

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
            text.write("\n")
            text.write(function)

        return text

    def _register_file(self, addon):
        ctx = bpy.context.copy()
        ctx["edit_text"] = addon
        bpy.ops.text.run_script(ctx)

    def _draw_errors(self):
        for error in self._errors:
            log = error_logs[error[0]]
            add_error_prop(log["title"],log["message"],log["fatal"],error[1].name)

    def autocompile(self):
        if sn_props().auto_compile:
            self.recompile()

    def recompile(self):
        tree = bpy.context.space_data.node_tree
        if self._is_scripting_tree():

            self._reset()

            self._compile_functions(tree)
            
            self._compile_operators(tree)

            self._compile_interface(tree)

            self._draw_errors()

            addon = self._create_file(tree)

            self._register_file(addon)

            bpy.context.area.tag_redraw()