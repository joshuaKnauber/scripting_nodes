import bpy
from .compiler_data import CompilerData

class ScriptingNodesCompiler():

    # CALLABLE FUNCTIONS
    # compile_active: takes the active node tree and compiles it after unregistering
    # compile_tree: recompiles the given tree
    # autocompile_active: compiles the active node tree if autocompile is active
    # unregister_active: unregisters the active node tree
    # unregister_all: unregisters all registered node trees
    # is_active_compiled: returns if the active node tree is compiled and registered
    # unregister_existing: tries to find registered addons in the file and removes them
    # get_export_file: returns a file for exporting the addon

    def __init__(self):
        self._indents = 4 # the number of indents that should be used in the generated files
        self._modules = [] # the currently registered modules
        self._run_register = True # runs register on compile
        self._hide_file = False # adds a dot in front of the file name to hide it

    def _only_string_in_line(self, line):
        """ returns if there are only strings in the given line """
        for snippet in line:
            if type(snippet) != str:
                return False
        return True

    def _compile_line(self, line, indents):
        """ compiles the given line and returns it as a string """
        while not self._only_string_in_line(line):
            for index, snippet in enumerate(line):
                if not type(snippet) == str:
                    line[index] = self._get_node_code(snippet.node, snippet, indents)
                    break
        return " "*indents + ("").join(line)

    def _compile_socket(self, socket, indents):
        """ compiles the given socket """
        return self._get_node_code(socket.node, socket, indents)

    def _compile_lines(self, lines, indents):
        """ compile the given lines """
        code = ""
        for line in lines:
            if type(line) == list:
                if line:
                    line = self._compile_line(line, indents)
                    code += line + "\n"
            elif type(line) == dict:
                code += self._compile_code_block(line, indents)
            else:
                code += self._compile_socket(line, indents)
        return code

    def _compile_code_block(self, block, indents):
        """ compiles the given code block """
        lines = self._compile_lines(block["lines"], indents)
        indented = self._compile_lines(block["indented"], indents + self._indents)
        return lines + indented

    def _get_node_code(self, node, output, indents):
        """ returns the code block for the given node """
        node_code = ""
        node_data = node.evaluate(output)
        for block in node_data["blocks"]:
            node_code += self._compile_code_block(block, indents)
        self._add_errors_to_active(node_data["errors"])
        return node_code

    def _add_errors_to_active(self, errors):
        """ adds the given errors to the active modules error list """
        for module in self._modules:
            if module["node_tree"] == bpy.context.space_data.node_tree:
                module["errors"] += errors

    def _get_registerable_node_blocks(self, tree):
        """ returns the code for the nodes that need to be registered """
        code_blocks = []
        for node in tree.nodes:
            if node._should_be_registered:
                code_blocks.append(self._get_node_code(node, None, 0))
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
                for line in node.get_register_block():
                    has_registered_nodes = True
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
                for line in node.get_unregister_block():
                    has_registered_nodes = True
                    unregister_function += "\n" + " "*self._indents + line

        if not has_registered_nodes:
            unregister_function += "\n" + " "*self._indents + "pass"
        return unregister_function

    def _write_paragraphs(self, text, amount):
        """ writes the given amount of paragraphs to the given file """
        for _ in range(amount):
            text.write("\n")

    def _create_addon_text(self, tree, is_export=False):
        """ creates the text for the addon with the given tree """
        if self._hide_file and not is_export:
            text = bpy.data.texts.new("." + tree.get_file_name())
        else:
            if is_export:
                text = bpy.data.texts.new("sn_"+tree.get_file_name())
            else:
                text = bpy.data.texts.new(tree.get_file_name())
        text.is_sn_addon = True
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
        module = {
            "node_tree": tree,
            "text": None,
            "module": None,
            "errors": []
        }
        self._modules.append(module)

        text = self._create_addon_text( tree )
        module = None
        if self._run_register:
            module = text.as_module()
        self._modules[-1]["text"] = text
        self._modules[-1]["module"] = module

    def _register_tree(self, tree):
        """ finds the matching module and registers it """
        for module in self._modules:
            if module["node_tree"] == tree:
                if self._run_register:
                    module["module"].register()

    def _unregister_tree(self, tree):
        """ unregisters the module if already registered and removes it """
        for module in self._modules:
            if module[ "node_tree" ] == tree:
                if self._run_register:
                    module[ "module" ].unregister()
                bpy.data.texts.remove(module["text"])
                self._modules.remove(module)
                break

    def _recompile(self, tree):
        """ compiles the active node tree """
        self._unregister_tree(tree)
        self._create_module(tree)
        self._register_tree(tree)

        if bpy.context.area:
            bpy.context.area.tag_redraw()

    def compile_active(self):
        """ recompiles the active tree """
        self._recompile(bpy.context.space_data.node_tree)

    def compile_tree(self, tree):
        """ recompiles the given tree """
        self._recompile(tree)

    def unregister_active(self):
        """ unregisters the active node trees module and removes it """
        self._unregister_tree(bpy.context.space_data.node_tree)

    def unregister_all(self):
        """ unregisters all registered node trees """
        for module in self._modules:
            self._unregister_tree(module["node_tree"])

    def autocompile_active(self):
        """ runs compile if the auto compile is enabled """
        if bpy.context.scene.sn_properties.auto_compile:
            self.compile_active()

    def socket_update(self, context):
        """ runs autocompile for a socket update """
        self.autocompile_active()

    def is_active_compiled(self):
        """ returns if the active node tree is compiled """
        for module in self._modules:
            if module["node_tree"] == bpy.context.space_data.node_tree:
                return True
        return False

    def unregister_existing(self):
        """ tries to find registered files in the addon and removes them """
        for text in bpy.data.texts:
            if text.is_sn_addon:
                try:
                    text.as_module().unregister()
                    bpy.data.texts.remove(text)
                except:
                    pass

    def get_export_file(self):
        """ returns the text for exporting the active node tree """
        return self._create_addon_text(bpy.context.space_data.node_tree, True)

    def get_active_addons_errors(self):
        """ returns the list of errors from the active node tree """
        for module in self._modules:
            if module["node_tree"] == bpy.context.space_data.node_tree:
                return module["errors"]
        return []


global_compiler = ScriptingNodesCompiler()
def compiler():
    global global_compiler
    return global_compiler