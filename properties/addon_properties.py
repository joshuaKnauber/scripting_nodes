import bpy
from .examples import handle

class ScriptingNodesProperties(bpy.types.PropertyGroup):

    def update_autocompile(self, context):
        context.space_data.node_tree.compiler.autocompile()

    def update_examples(self, context):
        handle(context, self.examples)

        if not self.examples == "None":
            self.examples = "None"

    auto_compile: bpy.props.BoolProperty(default=False,name="Auto Reload",description="Automatically reload the node tree on change",update=update_autocompile)

    examples: bpy.props.EnumProperty(
        items=[("None", "Examples", "Examples"),
               ("add_monkey", "Monkey adder", "Creates a button that makes a monkey"),
               ("add_monkey_size", "Monkey adder choose size", "Creates a button that makes a monkey with chooseble size")],
        name="Examples",
        description="Example Node Trees",
        update = update_examples
    )

    show_line_width: bpy.props.BoolProperty(default=False,name="Show settings",description="Show settings for the error panel")

    line_width: bpy.props.IntProperty(default=10,min=1,max=50,name="Error line breaks",description="How often the error message lines should break to the next line")


bpy.utils.register_class(ScriptingNodesProperties)
bpy.types.Scene.sn_properties = bpy.props.PointerProperty(type=ScriptingNodesProperties)
