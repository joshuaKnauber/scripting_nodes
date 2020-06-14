import bpy

class ScriptingNodesCompiler():

    def __init__(self):
        self._indents = 4 # the number of indents that should be used in the generated files
        self._modules = [] # the currently registered modules

    def autocompile(self):
        """ runs compile if the auto comile is enabled """
        if bpy.context.scene.sn_properties.auto_compile:
            self.recompile()

    def _unregister_tree(self, tree):
        """ unregisters the module if already registered """
        for module in self._modules:
            if module[ "node_tree" ] == tree:
                module[ "module" ].unregister()

    def recompile(self):
        """ compiles the active node tree """
        tree = bpy.context.space_data.node_tree

        #self._unregister_tree( tree )

        bpy.context.area.tag_redraw()


global_compiler = ScriptingNodesCompiler()
def compiler():
    global global_compiler
    return global_compiler