import bpy

class ScriptingNodesCompiler():

    # CALLABLE FUNCTIONS
    # compile_active: takes the active node tree and compiles it after unregistering
    # autocompile_active: compiles the active node tree if autocompile is active
    # unregister_active: unregisters the active node tree
    # unregister_all: unregisters all registered node trees

    def __init__(self):
        self._indents = 4 # the number of indents that should be used in the generated files
        self._modules = [] # the currently registered modules

    def _create_addon_text(self, tree):
        """ creates the text for the addon with the given tree """
        text = bpy.data.texts.new(".test")
        return text

    def _create_module(self, tree):
        """ generates the code from the node tree and adds it as a module """
        text = self._create_addon_text( tree )
        module = {
            "node_tree": tree,
            "text": text,
            "module": text.as_module()
        }
        self._modules.append(module)

    def _register_tree(self, tree):
        """ finds the matching module and registers it """
        for module in self._modules:
            if module["tree"] == tree:
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
            self._unregister_tree(module["tree"])

    def autocompile_active(self):
        """ runs compile if the auto comile is enabled """
        if bpy.context.scene.sn_properties.auto_compile:
            self.compile_active()


global_compiler = ScriptingNodesCompiler()
def compiler():
    global global_compiler
    return global_compiler