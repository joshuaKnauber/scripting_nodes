import bpy
from .compiler_data import CompilerData
from random import choice
from string import ascii_uppercase, ascii_lowercase

class ScriptingNodesCompiler():

    # CALLABLE FUNCTIONS
    # compile_active: takes the active node tree and compiles it after unregistering
    # compile_tree: recompiles the given tree
    # unregister_active: unregisters the active node tree
    # unregister_all: unregisters all registered node trees
    # is_active_compiled: returns if the active node tree is compiled and registered
    # unregister_existing: tries to find registered addons in the file and removes them
    # get_export_file: returns a file for exporting the addon
    # run_fuction: runs a function

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
                    line[index] = self._get_node_code(snippet.node, snippet, 0).rstrip()
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
                    if len(line) == 1 and type(line[0]) != str:
                        code += self._compile_socket(line[0], indents)
                    else:
                        code += self._compile_line(line, indents) + "\n"
                        
            elif type(line) == dict:
                code += self._compile_code_block(line, indents)
        return code

    def _compile_code_block(self, block, indents):
        """ compiles the given code block """
        lines = self._compile_lines(block["lines"], indents)
        indented = self._compile_lines(block["indented"], indents + self._indents)
        return lines + indented

    def _get_node_code(self, node, output, indents):
        """ returns the code block for the given node """
        node_code = ""
        input_output_data, errors = node.get_node_data()
        node_data = node.evaluate(output,input_output_data,errors)
        for block in node_data["blocks"]:
            node_code += self._compile_code_block(block, indents)
        self._add_errors_to_active(node_data["errors"])
        return node_code

    def _add_errors_to_active(self, errors):
        """ adds the given errors to the active modules error list """
        if bpy.context.space_data:
            for module in self._modules:
                if module["node_tree"] == bpy.context.space_data.node_tree:
                    module["errors"] += errors

    def _get_registerable_node_blocks(self, tree):
        """ returns the code for the nodes that need to be registered """
        code_blocks = []
        for node in tree.nodes:
            if hasattr(node, "should_be_registered"):
                if node.should_be_registered:
                    code_blocks.append(self._get_node_code(node, None, 0))
        return code_blocks

    def _get_needed_imports(self, tree):
        """ returns the import block """
        imports = ["bpy"]
        for node in tree.nodes:
            if hasattr(node, "required_imports"):
                for needed_import in node.required_imports():
                    if not needed_import in imports:
                        imports.append(needed_import)
        import_block = ""
        for needed_import in imports:
            import_block += "\nimport " + needed_import
        return import_block

    def _get_register_function(self, tree):
        """ returns the register function for the given node tree """
        register_function = CompilerData().register_block()

        if self._get_variable_registers(tree):
            register_function += "\n" + " "*self._indents + "# Register variables"
            register_function += "\n" + " "*self._indents + "bpy.utils.register_class(ArrayCollection_UID_)"
            register_function += "\n" + " "*self._indents + "bpy.utils.register_class(GeneratedAddonProperties_UID_)"
            register_function += "\n" + " "*self._indents + "bpy.types.Scene.sn_generated_addon_properties_UID_" + " = bpy.props.PointerProperty(type=GeneratedAddonProperties_UID_)"
            register_function += "\n" + " "*self._indents + "bpy.app.handlers.load_post.append(check_variables)\n"

        has_nodes = False
        for node in tree.nodes:
            if hasattr(node,"should_be_registered"):
                if node.should_be_registered:
                    for line in node.get_register_block():
                        register_function += "\n" + " "*self._indents + line
                        has_nodes = True
        
        if not has_nodes and not "sn_generated_addon_properties" in register_function:
            register_function += "\n" + " "*self._indents + "pass"

        return register_function

    def _get_variable_registers(self, tree):
        """ returns the variable registers for the given node tree """
        variable_ids = ["SN_BooleanVariableNode", "SN_FloatVariableNode", "SN_IntegerVariableNode", "SN_StringVariableNode", "SN_VectorVariableNode", "SN_EnumVariableNode"]
        register_function = ""

        for node in tree.nodes:
            if node.bl_idname in variable_ids:
                register_function += "\n" + " "*self._indents + node.get_variable_line()

        return register_function

    def _get_array_registers(self, tree):
        """ returns the variable registers for the given node tree """
        variable_ids = ["SN_BooleanVariableNode", "SN_FloatVariableNode", "SN_IntegerVariableNode", "SN_StringVariableNode", "SN_VectorVariableNode", "SN_EnumVariableNode"]
        register_function = "# Set the addons array variables\ndef set_variables():"

        has_nodes = False
        for node in tree.nodes:
            if node.bl_idname in variable_ids:
                for line in node.get_array_line():
                    register_function += "\n" + " "*self._indents + line
                    has_nodes = True
        
        if not has_nodes:
            register_function += "\n" + " "*self._indents + "pass"
                    
        return register_function

    def _get_unregister_function(self, tree):
        """ returns the unregister function for the given node tree """
        unregister_function = CompilerData().unregister_block()

        if self._get_variable_registers(tree):
            unregister_function += "\n" + " "*self._indents + "# Unregister variables"
            unregister_function += "\n" + " "*self._indents + "bpy.utils.unregister_class(ArrayCollection_UID_)"
            unregister_function += "\n" + " "*self._indents + "bpy.utils.unregister_class(GeneratedAddonProperties_UID_)"
            unregister_function += "\n" + " "*self._indents + "del bpy.types.Scene.sn_generated_addon_properties_UID_"
            unregister_function += "\n" + " "*self._indents + "bpy.app.handlers.load_post.remove(check_variables)\n"

        has_nodes = False
        for node in tree.nodes:
            if hasattr(node,"should_be_registered"):
                if node.should_be_registered:
                    for line in node.get_unregister_block():
                        unregister_function += "\n" + " "*self._indents + line
                        has_nodes = True
        
        if not has_nodes and not "ArrayCollection" in unregister_function:
            unregister_function += "\n" + " "*self._indents + "pass"

        return unregister_function

    def _using_cast(self, tree):
        identifiers = ["SN_CastFloatNode", "SN_CastVectorNode", "SN_CastStringNode", "SN_CastIntegerNode"]

        for node in tree.nodes:
            if node.bl_idname in identifiers:
                return True
        
        return False

    def _write_paragraphs(self, text, amount):
        """ writes the given amount of paragraphs to the given file """
        for _ in range(amount):
            text.write("\n")

    def write_addon_info(self,text,tree):
        name = tree.addon_name
        if not name:
            name = "My Addon"
        author = tree.addon_author
        description = tree.addon_description
        location = tree.addon_location
        wiki = tree.addon_wiki
        warning = tree.addon_warning
        category = tree.addon_category
        blender = "("+str(tree.addon_blender[0])+","+str(tree.addon_blender[1])+","+str(tree.addon_blender[2])+")"
        version = "("+str(tree.addon_version[0])+","+str(tree.addon_version[1])+","+str(tree.addon_version[2])+")"
        text.write("bl_info = {\n"+
                    " "*self._indents + f"\"name\": \"{name}\",\n"+
                    " "*self._indents + f"\"author\": \"{author}\",\n"+
                    " "*self._indents + f"\"description\": \"{description}\",\n"+
                    " "*self._indents + f"\"location\": \"{location}\",\n"+
                    " "*self._indents + f"\"doc_url\": \"{wiki}\",\n"+
                    " "*self._indents + f"\"warning\": \"{warning}\",\n"+
                    " "*self._indents + f"\"category\": \"{category}\",\n"+
                    " "*self._indents + f"\"blender\": {blender},\n"+
                    " "*self._indents + f"\"version\": {version}\n"+
                    "}")
        self._write_paragraphs(text,2)

    def _create_addon_text(self, tree, is_export=False):
        """ creates the text for the addon with the given tree """
        if self._hide_file and not is_export:
            text = bpy.data.texts.new("." + tree.name + " - " + tree.get_file_name())
        else:
            if is_export:
                text = bpy.data.texts.new("sn_"+tree.get_file_name())
            else:
                text = bpy.data.texts.new(tree.name + " - " + tree.get_file_name())
        text.is_sn_addon = True
        cd = CompilerData()

        text.write(cd.license_block())
        self._write_paragraphs(text, 2)
        text.write(cd.scripting_nodes_block())
        self._write_paragraphs(text,2)

        self.write_addon_info(text,tree)

        text.write(cd.comment_block("IMPORTS"))
        text.write(self._get_needed_imports(tree))
        text.write("\nfrom bpy.app.handlers import persistent")
        self._write_paragraphs(text,2)

        if self._using_cast(tree):
            text.write(cd.comment_block("UTILITY FUNCTIONS"))
            text.write(cd.utility_block())
            self._write_paragraphs(text,2)

        var_registers = self._get_variable_registers(tree)
        if var_registers:
            text.write(cd.comment_block("CLASSES"))
            text.write("# Create Array Collection for use in PROPERTIES\nclass ArrayCollection_UID_(bpy.types.PropertyGroup):\n"+ " "*self._indents +"string: bpy.props.StringProperty()\n"+ " "*self._indents +"bool: bpy.props.BoolProperty()\n"+ " "*self._indents +"int: bpy.props.IntProperty()\n"+ " "*self._indents +"float: bpy.props.FloatProperty()\n"+ " "*self._indents +"vector: bpy.props.FloatVectorProperty()\n"+ " "*self._indents +"four_vector: bpy.props.FloatVectorProperty(size=4)\n")
            self._write_paragraphs(text,1)

        text.write(cd.comment_block("CODE"))

        for block in self._get_registerable_node_blocks(tree):
            text.write(block)

        text.write(cd.comment_block("PROPERTIES"))
        if var_registers:
            text.write("# Store the addons variables\nclass GeneratedAddonProperties_UID_(bpy.types.PropertyGroup):\n" + " "*self._indents + "set_default: bpy.props.BoolProperty(default=True)")
            text.write(var_registers)
            text.write("\n\n# Check and set if the variable default values\n@persistent\ndef check_variables(dummy):\n"+" "*self._indents+"if bpy.context.scene.sn_generated_addon_properties_UID_" + ".set_default:\n" + " "*self._indents*2 + "bpy.context.scene.sn_generated_addon_properties_UID_" + ".set_default = False\n" + " "*self._indents*2 + "set_variables()\n")
            self._write_paragraphs(text,1)
            text.write(self._get_array_registers(tree))
            self._write_paragraphs(text,3)

        text.write(cd.keymap_block())
        self._write_paragraphs(text,2)

        text.write(cd.comment_block("REGISTER / UNREGISTER"))

        text.write(self._get_register_function(tree))
        self._write_paragraphs(text,2)
        text.write(self._get_unregister_function(tree))
        text_string = text.as_string().replace("UID_", "UID_"+tree.uid)
        text.clear()
        text.write(text_string)

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
        bpy.context.scene.sn_properties.print_texts.clear()

        for module in self._modules:
            if module[ "node_tree" ] == tree:
                if self._run_register:
                    module[ "module" ].unregister()
                bpy.data.texts.remove(module["text"])
                self._modules.remove(module)
                break

    def _recompile(self, tree):
        """ compiles the active node tree """
        tree.uid = choice(ascii_uppercase)
        for _ in range(7):
            tree.uid += choice(ascii_lowercase)

        self._unregister_tree(tree)
        self._create_module(tree)
        self._register_tree(tree)

        tree.use_fake_user = True

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
                except:
                    pass
                bpy.data.texts.remove(text)

    def get_export_file(self):
        """ returns the text for exporting the active node tree """
        return self._create_addon_text(bpy.context.space_data.node_tree, True)

    def get_active_addons_errors(self):
        """ returns the list of errors from the active node tree """
        if bpy.context.space_data:
            for module in self._modules:
                if module["node_tree"] == bpy.context.space_data.node_tree:
                    return module["errors"]
        return []

    def run_function(self, function_name):
        self.compile_active()
        for module in self._modules:
            if module[ "node_tree" ] == bpy.context.space_data.node_tree:
                eval("module[ 'module' ]." + function_name + "()")

global_compiler = ScriptingNodesCompiler()
def compiler():
    global global_compiler
    return global_compiler