import bpy

_unregister = None


class ScriptingNodesTree(bpy.types.NodeTree):
    bl_idname = "ScriptingNodeTree"
    bl_label = "Visual Scripting Editor"
    bl_icon = "FILE_SCRIPT"
    is_sn = True
    type: bpy.props.EnumProperty(
        items=[("SCRIPTING", "Scripting", "Scripting")], name="Type"
    )

    def update(self):
        """ Called when the node tree is updating. """

    def temp_build(self):
        global _unregister
        # TEMP
        code = "import bpy\n"
        register = ""
        unregister = ""
        for node in self.nodes:
            if node.code_register:
                code += node.code.strip() + "\n"
                register += " "*4 + node.code_register.strip() + "\n"
                unregister += " "*4 + node.code_unregister.strip() + "\n"

        code += "\n"
        code += "def register():\n"
        code += register
        code += "\n"
        code += "def unregister():\n"
        code += unregister
        code += "\n"

        if _unregister:
            _unregister()

        script = bpy.data.texts.new("script.py")
        script.write(code)
        module = script.as_module()
        module.register()
        _unregister = module.unregister

    def compile(self, node: bpy.types.Node):
        node.generate(bpy.context)
        self.temp_build()
