import bpy
import os
import json
from ...operators.tutorial_ops import get_tut_images
from ...handler.depsgraph import handle_depsgraph_update


class PrintProperties(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty()

class SearchVariablesGroup(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="item_name_placeholder")
    description: bpy.props.StringProperty(default="")
    type: bpy.props.StringProperty(default="")
    socket_type: bpy.props.StringProperty(default="")
    is_array: bpy.props.BoolProperty(default=False)
    identifier: bpy.props.StringProperty(default="")

class ScriptingNodesProperties(bpy.types.PropertyGroup):

    def update_examples(self, context):
        """ updates the examples """
        if self.examples != "NONE":
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"examples.json"), encoding="utf-8") as examples:
                examples = json.load(examples)
                example = examples[self.examples]
                
                path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"examples.blend")

                with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
                    data_to.node_groups = [example["tree_name"]]

                if example["tree_name"] in bpy.data.node_groups:
                    context.space_data.node_tree = bpy.data.node_groups[example["tree_name"]]
            self.examples = "NONE"

    example_cache = []

    def example_items(self, context):
        """ returns the example items """
        if self.example_cache:
            return self.example_cache
        else:
            items = [("NONE","Choose an example","Choose an example addon","PRESET",0)]
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"examples.json"), encoding="utf-8") as examples:
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

    # operator search
    operator_properties: bpy.props.CollectionProperty(type=SearchVariablesGroup)

    # defines if the node info should be shown
    def update_node_info(self,context):
        if self.show_node_info:
            self.show_tutorial = False
            bpy.ops.scripting_nodes.draw_docs("INVOKE_DEFAULT")

    def update_tutorial_info(self,context):
        if self.show_tutorial:
            self.tut_index = 0
            self.show_node_info = False
            bpy.ops.scripting_nodes.draw_tutorial("INVOKE_DEFAULT")

    def update_tut_index(self,context):
        if self.tut_index > len(get_tut_images())-1:
            self.show_tutorial = False
        elif self.tut_index < 0:
            self.tut_index = 0

    show_node_info: bpy.props.BoolProperty(default=False,update=update_node_info, name="Show Node Docs", description="This will show the documentation for the nodes")

    show_tutorial: bpy.props.BoolProperty(default=False,update=update_tutorial_info, name="Show Tutorial", description="This will show the tutorial")
    tut_index: bpy.props.IntProperty(default=0,update=update_tut_index)

    tutorial_scale: bpy.props.FloatProperty(default=1,min=0.1, soft_max=5, name="Docs Scale", description="The scale of the drawn UI elements")
    show_python_docs: bpy.props.BoolProperty(default=True,name="Show Python Docs",description="Shows the python code if the documentation is enabled")


    # showing the append panel selector
    showing_add_to_panel: bpy.props.BoolProperty(default=False)


    # recording a shortcut
    recording_shortcut: bpy.props.BoolProperty(default=False)


    # record action
    def update_record_action(self,context):
        if self.recording_action:
            pass

        else:
            old_type = context.area.type
            context.area.type = "INFO"
            bpy.ops.info.select_all()
            bpy.ops.info.report_copy()
            context.area.type = old_type

            actions = bpy.context.window_manager.clipboard.split("bpy.context.scene.sn_properties.recording_action = True")[-1].splitlines()
            action_nodes = []
            for action in actions:

                node = None
                if "(" in action and ")" in action: # process operator
                    action = action.split(".")[2] + "." + action.split(".")[3].split("(")[0]
                    node = context.space_data.node_tree.nodes.new("SN_RunOperator")
                    node.search_prop = "internal"

                    for cat in dir(bpy.ops):
                        try:
                            if cat != "scripting_nodes" and not cat[0].isnumeric():
                                for op in dir(eval("bpy.ops."+cat)):
                                    if not op[0].isnumeric():
                                        if cat + "." + op == action:
                                            for item in context.scene.sn_properties.operator_properties:
                                                if item.identifier == action:
                                                    node.propName = item.name
                        except:pass

                    if node.propName: # set operator properties
                        pass

                elif "=" in action: # process property
                    pass
                
                if node: # process node
                    action_nodes.append(node)

            # place nodes
            for node in context.space_data.node_tree.nodes:
                node.select = False
            node_loc = [0,0]
            for node in action_nodes:
                node.location = tuple(node_loc)
                node_loc[0] += node.width + 50
                node.select = True

    recording_action: bpy.props.BoolProperty(default=False,name="Record Actions",update=update_record_action)