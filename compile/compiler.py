import bpy
from .compiler_data import gpl_block, addon_info, error_logs, import_texts, register_text
from ..properties.property_utils import clear_error_props, add_error_prop, sn_props

class ScriptingNodesCompiler():

    def __init__(self):
        self._indents = 4
        self._errors = []
        self._functions = []
        self._operators = []
        self._interface = []

    def _is_scripting_tree(self):
        #returns if the current tree is a scripting tree
        if bpy.context.space_data.tree_type == 'ScriptingNodesTree':
            return bpy.context.space_data.node_tree != None
    
    def _unregister(self):
        for registered in self._interface + self._operators:
            idname = registered.split(":")[0].split("(")[0].split(" ")[-1]
            if hasattr(bpy.types,idname):
                bpy.utils.unregister_class(eval("bpy.types." + idname))

    def _reset(self):
        #resets the compiler data and errors
        self._unregister()
        clear_error_props()
        self._errors.clear()
        self._functions.clear()
        self._interface.clear()
        self._operators.clear()

    def _only_string(self, value_list):
        #returns if the given list contains only strings
        for value in value_list:
            if not type(value) == str:
                return False
        return True

    def _compile_script_line(self, line):
        #goes through every entry in the line while it contains node references
        #it calls evaluate on the nodes that are still in the list
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

        #add indents if in line
        for i, snippet in enumerate(line):
            line[i] = snippet.replace("_INDENT_"," "*self._indents)
        return line

    def _compile_tree_branch(self, function_node, indents, evaluate_start_node, only_evaluate_start_node):
        code_blocks = ""
        continue_program = True

        while continue_program and not only_evaluate_start_node or evaluate_start_node:

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

            if "functions" in function_value:
                for func in function_value["functions"]:
                    if func["socket"]:
                        function_result = self._compile_tree_branch(func["socket"].node,self._indents*2,True,False)
                        function_result += " "*self._indents*2 + func["followup"]
                        code_block += [function_result]

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
        #compiles all functions in the node tree
        function_nodes = []
        
        #finds all function nodes
        for node in tree.nodes:
            if node.bl_idname == "SN_FunctionNode":
                function_nodes.append(node)

        #compiles the tree branch for every function node and adds the code string to the list
        for function_node in function_nodes:
            function = self._compile_tree_branch(function_node,0,True,True)
            self._functions.append(function)

    def _compile_operators(self, tree):
        #compiles all operators in the node tree
        operator_nodes = []

        #finds all operator nodes in the node tree
        for node in tree.nodes:
            if node.bl_idname == "SN_OperatorNode":
                operator_nodes.append(node)

        for operator in operator_nodes:
            operator = self._compile_tree_branch(operator,0,True,True)
            self._operators.append(operator)

    def _compile_interface(self, tree):
        #compiles all interface nodes in the node tree
        panel_nodes = []
        
        #finds all function nodes
        for node in tree.nodes:
            if node.bl_idname == "SN_UiPanelNode":
                panel_nodes.append(node)

        for panel in panel_nodes:
            panel = self._compile_tree_branch(panel,0,True,True)
            self._interface.append(panel)

    def _create_file(self, tree):
        name = tree.addon_name.lower().replace(" ","_") + ".py"

        #creates the python file for the addon
        if not name in bpy.data.texts:
            bpy.data.texts.new(name=name)
        text = bpy.data.texts[name]

        text.clear()

        #writes all basic in the text fie
        text.write(gpl_block)
        text.write("\n")
        text.write(addon_info(tree))
        text.write("\n\n")
        text.write(import_texts)
        text.write("\n")
        
        #writes all functions in the text file
        for function in self._functions:
            text.write("\n")
            text.write(function)

        #writes all operators in the text file
        for operator in self._operators:
            text.write("\n")
            text.write(operator)

        #writes all interfaces in the text file
        for interface in self._interface:
            text.write("\n")
            text.write(interface)

        #write classes
        text.write("\nclasses = [\n")
        for register in self._interface + self._operators:
            idname = register.split(":")[0].split("(")[0].split(" ")[-1]
            text.write(" "*self._indents + idname + ",\n")
        text.write("]\n\n")

        #register function
        text.write(register_text(self._indents,False))
        text.write("\n\n")

        #unregister function
        text.write(register_text(self._indents,True))

        #call register
        text.write("\n\n")
        text.write("if __name__ == '__main__':\n")
        text.write(" "*self._indents + "register()")

        return text

    def _register_file(self, addon):
        #registers the addon in the blend file
        ctx = bpy.context.copy()
        ctx["edit_text"] = addon
        #bpy.ops.text.run_script(ctx)
        #bpy.data.texts.remove(addon)

    def _draw_errors(self):
        #adds all the errors from the error list to the props
        for error in self._errors:
            log = error_logs[error[0]]
            add_error_prop(log["title"],log["message"],log["fatal"],error[1].name)

    def autocompile(self):
        #checks if autocompile is on and runs compile
        #this should be called when changes to the node tree are made
        if sn_props().auto_compile:
            self.recompile()

    def recompile(self):
        #compiles the node tree to code and registers the file
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