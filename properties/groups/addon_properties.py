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
            execute_inputs = []
            execute_outputs = []
            for action in actions:

                node = None
                if "bpy.ops" in action and "(" in action and ")" in action: # process operator
                    properties = []
                    values = []

                    items = []
                    for x, prop_string in enumerate("(".join(action.split("(")[1:])[:-1].split("=")):
                        if x == 0 or x == len("(".join(action.split("(")[1:])[:-1].split("="))-1:
                            items.append(prop_string.strip())
                        else:
                            items.append(",".join(prop_string.split(",")[:-1]).strip())
                            items.append(prop_string.split(",")[-1].strip())

                    for x, prop in enumerate(items):
                        if x%2 == 0:
                            properties.append(prop)
                        else:
                            values.append(prop)

                    action = action.split(".")[2] + "." + action.split(".")[3].split("(")[0]
                    node = context.space_data.node_tree.nodes.new("SN_RunOperator")
                    action_nodes.append(node)
                    execute_inputs.append(node.inputs[0])
                    execute_outputs.append(node.outputs[0])
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
                        except:
                            print("Something went wrong! Please check the generated node setup.")

                    if node.propName: # set operator properties
                        for x, property_id in enumerate(properties):
                            if property_id:
                                if eval("bpy.ops." + action + ".get_rna_type().properties['" + property_id + "'].type") != "ENUM":
                                    for inp in node.inputs:
                                        if property_id.replace("_", " ").title() == inp.name:
                                            # set value
                                            if eval("bpy.ops." + action + ".get_rna_type().properties['" + property_id + "'].type") in ["STRING", "BOOLEAN", "INT", "FLOAT"]:
                                                try:
                                                    inp.set_value(eval(values[x]))
                                                except:
                                                    print("Something went wrong! Please check the generated node setup.")

                                else:
                                    for enum in node.enum_collection:
                                        if enum.prop_identifier == property_id:
                                            enum.enum = eval(values[x])

                elif "bpy.data" in action or "bpy.context" in action:
                    action = action.replace("[0]", "")
                    action = action.replace("[1]", "")
                    action = action.replace("[2]", "")
                    is_dot_data = False
                    if "bpy.data" in action:
                        is_dot_data = True
                        value = action.split(" = ")[1]
                        action = action.split(" = ")[0].replace("bpy.data.", "")
                    else:
                        value = action.split(" = ")[1]
                        action = action.split(" = ")[0].replace("bpy.context.", "")
                    path = []

                    is_string = False
                    current_path = ""
                    for char in action:
                        if char == "\"":
                            is_string = not is_string
                        if not is_string:
                            if char == ".":
                                if current_path != "":
                                    path.append(current_path)
                                current_path = ""
                            elif char == "[":
                                if current_path != "":
                                    path.append(current_path)
                                current_path = "["
                            elif char == "]":
                                current_path+=char
                                if current_path != "":
                                    path.append(current_path)
                                current_path = ""
                            else:
                                current_path+=char
                        else:
                            current_path+=char
                    path.append(current_path)

                    if is_dot_data:
                        data_node = context.space_data.node_tree.nodes.new("SN_ObjectDataNode")
                        action_nodes.append(data_node)
                        is_collection = False
                        for dataType in bpy.data.rna_type.properties:
                            if dataType.identifier == path[0]:
                                is_collection = True
                                data_node.data_type_enum = path[0]
                        if not is_collection:
                            print("Something went wrong! Please check the generated node setup.")
                            break
                        node_socket = data_node.outputs[0]
                    else:
                        context_type = {"active_bone": "Active bone","active_object": "Active object","object": "Active object","active_pose_bone": "Active pose bone","area": "Area","collection": "Collection","pose_object": "Pose Object","region": "Region","scene": "Scene","screen": "Screen","view_layer": "View layer","window_manager": "Window manager","workspace": "Workspace", "preferences": "Preferences"}
                        context_node = context.space_data.node_tree.nodes.new("SN_ObjectContextNode")
                        action_nodes.append(context_node)

                        if path[0] in context_type:
                            node_socket = context_node.outputs[context_type[path[0]]]
                        else:
                            print("Something went wrong! Please check the generated node setup.")
                            break

                    for node_path in path[1:-1]:
                        if "[" in node_path:
                            node = context.space_data.node_tree.nodes.new("SN_GetDataPropertiesNode")
                            action_nodes.append(node)
                            context.space_data.node_tree.links.new(node.inputs[0], node_socket)
                            node.use_index = False
                            node.inputs[1].set_value(eval(node_path[1:-1]))
                        else:
                            node = context.space_data.node_tree.nodes.new("SN_GetDataPropertiesNode")
                            action_nodes.append(node)
                            context.space_data.node_tree.links.new(node.inputs[0], node_socket)
                            for prop in node.search_properties:
                                if node_path == prop.identifier:
                                    node.search_value = prop.name
                                    bpy.ops.scripting_nodes.add_scene_data_socket(node_name=node.name, socket_name=prop.name, is_output=True, use_four_numbers=node.search_properties[prop.name].use_four_numbers, is_color=node.search_properties[prop.name].is_color)

                        try:
                            node_socket = node.outputs[0]
                        except:
                            print("Something went wrong! Please check the generated node setup.")
                            break

                    node = context.space_data.node_tree.nodes.new("SN_SetDataPropertiesNode")
                    action_nodes.append(node)
                    execute_inputs.append(node.inputs[0])
                    execute_outputs.append(node.outputs[0])
                    context.space_data.node_tree.links.new(node.inputs[1], node_socket)

                    in_search_prop = False
                    for prop in node.search_properties:
                        if path[-1] == prop.identifier:
                            in_search_prop = True
                            node.search_value = prop.name
                            bpy.ops.scripting_nodes.add_scene_data_socket(node_name=node.name, socket_name=prop.name, is_output=False, use_four_numbers=node.search_properties[prop.name].use_four_numbers, is_color=node.search_properties[prop.name].is_color)
                            try:
                                node.inputs[2].set_value(eval(value))
                            except:
                                print("Something went wrong! Please check the generated node setup.")

                    if not in_search_prop:
                        try:
                            if type(eval(value)) == str:
                                bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="STRING")
                                node.inputs[2].set_value(eval(value))
                            elif type(eval(value)) == bool:
                                bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="BOOLEAN")
                                node.inputs[2].set_value(eval(value))
                            elif type(eval(value)) == int:
                                bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="INTEGER")
                                node.inputs[2].set_value(eval(value))
                            elif type(eval(value)) == float:
                                bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="FLOAT")
                                node.inputs[2].set_value(eval(value))
                            elif type(eval(value)) == tuple:
                                bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="VECTOR")
                                node.inputs[2].set_value(eval(value))
                            else:
                                print("Something went wrong! Please check the generated node setup.")
                        except:
                            print("Something went wrong! Please check the generated node setup.")

            if len(execute_inputs):
                execute_inputs.pop(0)
                for socket in range(len(execute_inputs)):
                    context.space_data.node_tree.links.new(execute_outputs[socket], execute_inputs[socket])

            # place nodes
            for node in context.space_data.node_tree.nodes:
                node.select = False
            node_loc = [0,0]
            for node in action_nodes:
                if node.bl_idname in ["SN_GetDataPropertiesNode", "SN_ObjectDataNode", "SN_ObjectContextNode"]:
                    node_loc[1] = -75
                else:
                    node_loc[1] = 0
                node.location = tuple(node_loc)
                node_loc[0] += node.width + 50
                node.select = True

    recording_action: bpy.props.BoolProperty(default=False,name="Record Actions",update=update_record_action)