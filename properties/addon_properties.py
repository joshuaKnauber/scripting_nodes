import bpy


class ScriptingNodesProperties(bpy.types.PropertyGroup):

    def update_autocompile(self, context):
        context.space_data.node_tree.compiler.autocompile()

    def udpate_examples(self, context):
        if not self.examples == "None":
            self.examples = "None"

    auto_compile: bpy.props.BoolProperty(default=False,name="Auto Reload",description="Automatically reload the node tree on change",update=update_autocompile)

    examples: bpy.props.EnumProperty(
        items=[("None", "Examples", "Examples"),
               ("add_monkey", "Monkey adder", "Creates a button that makes a monkey"),
               ("add_monkey_size", "Monkey adder choose size", "Creates a button that makes a monkey with chooseble size")],
        name="Examples",
        description="Example Node Trees",
        update = udpate_examples
    )


bpy.utils.register_class(ScriptingNodesProperties)
bpy.types.Scene.sn_properties = bpy.props.PointerProperty(type=ScriptingNodesProperties)
