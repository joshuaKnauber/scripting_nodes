import bpy
import os
import json
from ...handler.example_functions import import_example


class PrintProperties(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty()

class ScriptingNodesProperties(bpy.types.PropertyGroup):

    def update_auto_compile(self,context):
        """ function for updating the auto compile property """

    def update_examples(self, context):
        """ updates the examples """
        if self.examples != "NONE":
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"examples.json")) as examples:
                examples = json.load(examples)
                import_example(examples[self.examples],self.examples)
            self.examples = "NONE"

    example_cache = []

    def example_items(self, context):
        """ returns the example items """
        if self.example_cache:
            return self.example_cache
        else:
            items = [("NONE","Choose an example","Choose an example addon","PRESET",0)]
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"examples.json")) as examples:
                examples = json.load(examples)
                for index, key in enumerate(examples):
                    example = examples[key]
                    items.append((key,key,key,example["icon"],index+1))
            self.example_cache = items
            return items

    # if true the node tree gets recompiled on changes
    auto_compile: bpy.props.BoolProperty(default=False, name="Auto Reload", description="Automatically reloads the addon when changes are made", update=update_auto_compile)

    # show the line width property in the ui
    show_line_width: bpy.props.BoolProperty(default=False,name="Show settings",description="Show settings for the error panel")

    # the width of a line in the errors panel
    line_width: bpy.props.IntProperty(default=10,min=1,max=50,name="Error line breaks",description="How often the error message lines should break to the next line")

    # this is true when a package has been installed and blender hasn't been restarted yet
    package_installed_without_reload: bpy.props.BoolProperty(default=False)

    # this is true when a package has been uninstalled and blender hasn't been restarted yet
    package_uninstalled_without_reload: bpy.props.BoolProperty(default=False)

    # examples dropdown
    examples: bpy.props.EnumProperty(name="Examples",description="Example node trees for the addon",update=update_examples,items=example_items)

    # print texts
    print_texts: bpy.props.CollectionProperty(type=PrintProperties)