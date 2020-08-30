import bpy
import os
import json


class PrintProperties(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty()

class SearchVariablesGroup(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="item_name_placeholder")
    description: bpy.props.StringProperty(default="")
    type: bpy.props.StringProperty(default="")
    socket_type: bpy.props.StringProperty(default="")
    is_array: bpy.props.BoolProperty(default=False)

class ScriptingNodesProperties(bpy.types.PropertyGroup):

    def update_examples(self, context):
        """ updates the examples """
        if self.examples != "NONE":
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"examples.json")) as examples:
                examples = json.load(examples)
                pass
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

    def update_filters(self, context):
        for node in context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_DataPropertiesNode":
                node.update()

    # show the line width property in the ui
    show_line_width: bpy.props.BoolProperty(default=False,name="Show settings",description="Show settings for the error panel")

    # the width of a line in the errors panel
    line_width: bpy.props.IntProperty(default=10,min=1,max=50,name="Error line breaks",description="How often the error message lines should break to the next line")

    # this is true when a package has been installed and blender hasn't been restarted yet
    package_installed_without_compile: bpy.props.BoolProperty(default=False)

    # this is true when a package has been uninstalled and blender hasn't been restarted yet
    package_uninstalled_without_compile: bpy.props.BoolProperty(default=False)

    # examples dropdown
    examples: bpy.props.EnumProperty(name="Examples",description="Example node trees for the addon",update=update_examples,items=example_items)

    # print texts
    print_texts: bpy.props.CollectionProperty(type=PrintProperties)

    # properties for filtering data property search
    filter_string: bpy.props.BoolProperty(name="Show Strings in the search bar", default=True, update=update_filters)
    filter_bool: bpy.props.BoolProperty(name="Show Booleans in the search bar", default=True, update=update_filters)
    filter_int: bpy.props.BoolProperty(name="Show Integers in the search bar", default=True, update=update_filters)
    filter_float: bpy.props.BoolProperty(name="Show Floats in the search bar", default=True, update=update_filters)
    filter_vector: bpy.props.BoolProperty(name="Show Vectors in the search bar", default=True, update=update_filters)
    filter_data_block_collection: bpy.props.BoolProperty(name="Show Data Block Collections in the search bar", default=True, update=update_filters)
    filter_data_block: bpy.props.BoolProperty(name="Show Data Blocks in the search bar", default=True, update=update_filters)

    # variable search
    search_variables: bpy.props.CollectionProperty(type=SearchVariablesGroup)
    
    # enum search
    sn_enum_property_properties: bpy.props.CollectionProperty(type=SearchVariablesGroup)

    # defines if the node info should be shown
    def update_node_info(self,context):
        if self.show_node_info:
            bpy.ops.scripting_nodes.draw_tutorial("INVOKE_DEFAULT")
    show_node_info: bpy.props.BoolProperty(default=False,update=update_node_info)

    # defines if the marketplace should be shown
    def update_marketplace(self,context):
        if self.show_marketplace:
            bpy.ops.scripting_nodes.draw_marketplace("INVOKE_DEFAULT")
    show_marketplace: bpy.props.BoolProperty(default=False,update=update_marketplace)

    tutorial_scale: bpy.props.FloatProperty(default=1,min=0.1, soft_max=5)
