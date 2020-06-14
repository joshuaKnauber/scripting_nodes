import bpy
from .compiler_data import CompilerData

class ScriptingNodesCompiler():

    # CALLABLE FUNCTIONS
    # compile_active: takes the active node tree and compiles it after unregistering
    # autocompile_active: compiles the active node tree if autocompile is active
    # unregister_active: unregisters the active node tree
    # unregister_all: unregisters all registered node trees
    # is_active_compiled: returns if the active node tree is compiled and registered

    def __init__(self):
        self._indents = 4 # the number of indents that should be used in the generated files
        self._modules = [] # the currently registered modules

    def _only_string_in_line(self, line):
        """ returns if there are only strings in the given line """
        for snippet in line:
            if type(snippet) != str:
                return False
        return True

    def _compile_line(self,line):
        """ compiles the given line and returns it as a string """
        while not self._only_string_in_line(line):
            for index, snippet in enumerate(line):
                if not type(snippet) == str:
                    node_data = snippet.node.evaluate(snippet)
                    line[index] = self._compile_node_data(node_data)
                    break
        return ("").join(line)

    def _compile_block_lines(self, lines, indents):
        """ compiles the lines in a block code or indented """
        node_code = ""
        for line in lines:
            node_code += " "*indents + self._compile_line(line) + "\n"
        return node_code

    def _compile_code_block(self,block,previous_indents):
        """ compiles the given code block with the right amount of indents """
        node_code = ""
        node_code += self._compile_block_lines(block["lines"],previous_indents)
        node_code += self._compile_block_lines(block["indented"],previous_indents + self._indents)
        return node_code

    def _compile_node_data(self, node_data):
        """ returns the compiled node data """
        node_code = ""
        for block in node_data["blocks"]:
            node_code += self._compile_code_block(block,0)
        return node_code

    def _get_node_block(self, node):
        """ returns the code block for the given node """
        node_data = node.evaluate(None)
        return self._compile_node_data(node_data)

    def _get_registerable_node_blocks(self, tree):
        """ returns the code for the nodes that need to be registered """
        code_blocks = []
        for node in tree.nodes:
            if node._should_be_registered:
                code_blocks.append(self._get_node_block(node))
        return code_blocks

    def _get_needed_imports(self, tree):
        """ returns the import block """
        imports = []
        for node in tree.nodes:
            for needed_import in node.needed_imports():
                if not needed_import in imports:
                    imports.append(needed_import)
        import_block = ""
        for needed_import in imports:
            import_block += "\nimport " + needed_import
        return import_block

    def _get_register_function(self, tree):
        """ returns the register function for the given node tree """
        register_function = CompilerData().register_block()

        has_registered_nodes = False
        for node in tree.nodes:
            if node._should_be_registered:
                has_registered_nodes = True
                for line in node.get_register_block():
                    register_function += "\n" + " "*self._indents + line

        if not has_registered_nodes:
            register_function += "\n" + " "*self._indents + "pass"
        return register_function

    def _get_unregister_function(self, tree):
        """ returns the unregister function for the given node tree """
        unregister_function = CompilerData().unregister_block()

        has_registered_nodes = False
        for node in tree.nodes:
            if node._should_be_registered:
                has_registered_nodes = True
                for line in node.get_unregister_block():
                    unregister_function += "\n" + " "*self._indents + line

        if not has_registered_nodes:
            unregister_function += "\n" + " "*self._indents + "pass"
        return unregister_function

    def _write_paragraphs(self, text, amount):
        """ writes the given amount of paragraphs to the given file """
        for _ in range(amount):
            text.write("\n")

    def _create_addon_text(self, tree):
        """ creates the text for the addon with the given tree """
        text = bpy.data.texts.new(tree.get_file_name())
        cd = CompilerData()

        text.write(cd.license_block())
        self._write_paragraphs(text, 2)
        text.write(cd.scripting_nodes_block())
        self._write_paragraphs(text,2)
        text.write(self._get_needed_imports(tree))
        self._write_paragraphs(text,2)
        for block in self._get_registerable_node_blocks(tree):
            text.write(block)
            self._write_paragraphs(text,2)
        text.write(self._get_register_function(tree))
        self._write_paragraphs(text,2)
        text.write(self._get_unregister_function(tree))
        return text

    def _create_module(self, tree):
        """ generates the code from the node tree and adds it as a module """
        text = self._create_addon_text( tree )
        module = {
            "node_tree": tree,
            "text": text,
            "module": text.as_module(),
            "errors": []
        }
        self._modules.append(module)

    def _register_tree(self, tree):
        """ finds the matching module and registers it """
        for module in self._modules:
            if module["node_tree"] == tree:
                module["module"].register()

    def _unregister_tree(self, tree):
        """ unregisters the module if already registered and removes it """
        for module in self._modules:
            if module[ "node_tree" ] == tree:
                module[ "module" ].unregister()
                bpy.data.texts.remove(module["text"])
                self._modules.remove(module)
                break

    def _recompile(self, tree):
        """ compiles the active node tree """
        self._unregister_tree(tree)
        self._create_module(tree)
        self._register_tree(tree)

        bpy.context.area.tag_redraw()

    def compile_active(self):
        """ recompiles the active tree """
        self._recompile(bpy.context.space_data.node_tree)

    def unregister_active(self):
        """ unregisters the active node trees module and removes it """
        self._unregister_tree(bpy.context.space_data.node_tree)

    def unregister_all(self):
        """ unregisters all registered node trees """
        for module in self._modules:
            self._unregister_tree(module["node_tree"])

    def autocompile_active(self):
        """ runs compile if the auto comile is enabled """
        if bpy.context.scene.sn_properties.auto_compile:
            self.compile_active()

    def is_active_compiled(self):
        """ returns if the active node tree is compiled """
        for module in self._modules:
            if module["tree"] == bpy.context.space_data.node_tree:
                return True
        return False


global_compiler = ScriptingNodesCompiler()
def compiler():
    global global_compiler
    return global_compiler