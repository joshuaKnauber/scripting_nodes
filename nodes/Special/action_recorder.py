import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup


class SN_OT_RemoveAction(bpy.types.Operator):
    bl_idname = "sn.remove_action"
    bl_label = "Remove Action"
    bl_description = "Removes an action from the action recorder node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    index: bpy.props.IntProperty()
    node: bpy.props.StringProperty(options={"SKIP_SAVE"},default="")


    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        node.actions.remove(self.index)

        return {"FINISHED"}
    

class SN_RecorderNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RecorderNode"
    bl_label = "Action Recorder"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    actions: bpy.props.CollectionProperty(type=SN_GenericPropertyGroup)


    def on_create(self,context):
        self.add_execute_input("Action Recorder")
        self.add_execute_output("Execute").mirror_name = True

    def draw_node(self,context,layout):
        if not self.recording_action:
            layout.prop(self, "recording_action", text="Start Recording", toggle=True, icon="RADIOBUT_OFF")
        else:
            layout.prop(self, "recording_action", text="Stop Recording", toggle=True, icon="RADIOBUT_ON")

        if len(self.actions):
            box = layout.box()
            for x, action in enumerate(self.actions):
                row = box.row()
                row.operator("sn.question_mark", text="", icon="QUESTION", emboss=False).to_display = action.identifier
                row.label(text=action.name)
                op = row.operator("sn.remove_action", text="", icon="X", emboss=False)
                op.index = x
                op.node = self.name


    def update_record_action(self,context):
        if self.recording_action:
            pass
        else:
            old_type = context.area.type
            context.area.type = "INFO"
            bpy.ops.info.select_all()
            bpy.ops.info.report_copy()
            context.area.type = old_type

            recorded_actions = bpy.context.window_manager.clipboard.split('bpy.data.node_groups["' + self.node_tree.name + '"].nodes["' + self.name + '"].recording_action = True')[-1].splitlines()

            self.actions.clear()
            for action in recorded_actions:
                if action:
                    if "bpy.ops." in action:
                        new_action = self.actions.add()
                        name = action.split("(")[0].split(".")
                        new_action.name = name[-2].replace("_", " ").title() + " - " + eval(action.split("(")[0] + ".get_rna_type().name")
                        new_action.description = action
                        new_action.identifier = action

            return
                # if "bpy.ops" in action and "(" in action and ")" in action: # process operator
                #     properties = []
                #     values = []

                #     items = []
                #     for x, prop_string in enumerate("(".join(action.split("(")[1:])[:-1].split("=")):
                #         if x == 0 or x == len("(".join(action.split("(")[1:])[:-1].split("="))-1:
                #             items.append(prop_string.strip())
                #         else:
                #             items.append(",".join(prop_string.split(",")[:-1]).strip())
                #             items.append(prop_string.split(",")[-1].strip())

                #     for x, prop in enumerate(items):
                #         if x%2 == 0:
                #             properties.append(prop)
                #         else:
                #             values.append(prop)

                #     action = action.split(".")[2] + "." + action.split(".")[3].split("(")[0]
                #     node = context.space_data.node_tree.nodes.new("SN_RunOperator")
                #     if node_socket:
                #         context.space_data.node_tree.links.new(node_socket, node.inputs[0])
                #     node_socket = node.outputs[0]
                #     node.search_prop = "internal"

                #     for cat in dir(bpy.ops):
                #         try:
                #             if cat != "scripting_nodes" and not cat[0].isnumeric():
                #                 for op in dir(eval("bpy.ops."+cat)):
                #                     if not op[0].isnumeric():
                #                         if cat + "." + op == action:
                #                             for item in context.scene.sn_properties.operator_properties:
                #                                 if item.identifier == action:
                #                                     node.propName = item.name
                #         except:pass

                #     if node.propName: # set operator properties
                #         for x, property_id in enumerate(properties):
                #             if property_id:
                #                 if eval("bpy.ops." + action + ".get_rna_type().properties['" + property_id + "'].type") != "ENUM":
                #                     for inp in node.inputs:
                #                         if property_id.replace("_", " ").title() == inp.name:
                #                             # set value
                #                             if eval("bpy.ops." + action + ".get_rna_type().properties['" + property_id + "'].type") in ["STRING", "BOOLEAN", "INT", "FLOAT"]:
                #                                 inp.set_value(eval(values[x]))

                #                 else:
                #                     for enum in node.enum_collection:
                #                         if enum.prop_identifier == property_id:
                #                             enum.enum = eval(values[x])

                # elif "bpy.data" in action or "bpy.context" in action:
                #     is_dot_data = False
                #     if "bpy.data" in action:
                #         is_dot_data = True
                #         value = action.split(" = ")[1]
                #         action = action.split(" = ")[0].replace("bpy.data.", "")
                #     else:
                #         value = action.split(" = ")[1]
                #         action = action.split(" = ")[0].replace("bpy.context.", "")
                #     path = []

                #     is_string = False
                #     current_path = ""
                #     for char in action:
                #         if char == "\"":
                #             is_string = not is_string
                #         if not is_string:
                #             if char == ".":
                #                 if current_path != "":
                #                     path.append(current_path)
                #                 current_path = ""
                #             elif char == "[":
                #                 if current_path != "":
                #                     path.append(current_path)
                #                 current_path = "["
                #             elif char == "]":
                #                 current_path+=char
                #                 if current_path != "":
                #                     path.append(current_path)
                #                 current_path = ""
                #             else:
                #                 current_path+=char
                #         else:
                #             current_path+=char
                #     path.append(current_path)

                #     if is_dot_data:
                #         data_node = context.space_data.node_tree.nodes.new("SN_ObjectDataNode")
                #         is_collection = False
                #         for dataType in bpy.data.rna_type.properties:
                #             if dataType.identifier == path[0]:
                #                 is_collection = True
                #                 data_node.data_type_enum = path[0]
                #         if not is_collection:
                #             break
                #         node_socket = data_node.outputs[0]
                #     else:
                #         context_type = {"active_bone": "Active bone","active_object": "Active object","object": "Active object","active_pose_bone": "Active pose bone","area": "Area","collection": "Collection","pose_object": "Pose Object","region": "Region","scene": "Scene","screen": "Screen","view_layer": "View layer","window_manager": "Window manager","workspace": "Workspace"}
                #         context_node = context.space_data.node_tree.nodes.new("SN_ObjectContextNode")

                #         if path[0] in context_type:
                #             node_socket = context_node.outputs[context_type[path[0]]]
                #         else:
                #             break

                #     for node_path in path[1:-1]:
                #         if "[" in node_path:
                #             node = context.space_data.node_tree.nodes.new("SN_GetDataPropertiesNode")
                #             context.space_data.node_tree.links.new(node.inputs[0], node_socket)
                #             node.use_index = False
                #             node.inputs[1].set_value(eval(node_path[1:-1]))
                #         else:
                #             node = context.space_data.node_tree.nodes.new("SN_GetDataPropertiesNode")
                #             context.space_data.node_tree.links.new(node.inputs[0], node_socket)
                #             for prop in node.search_properties:
                #                 if node_path == prop.identifier:
                #                     node.search_value = prop.name
                #                     bpy.ops.scripting_nodes.add_scene_data_socket(node_name=node.name, socket_name=prop.name, is_output=True, use_four_numbers=node.search_properties[prop.name].use_four_numbers, is_color=node.search_properties[prop.name].is_color)

                #         node_socket = node.outputs[0]

                #     node = context.space_data.node_tree.nodes.new("SN_SetDataPropertiesNode")
                #     context.space_data.node_tree.links.new(node.inputs[1], node_socket)

                #     in_search_prop = False
                #     for prop in node.search_properties:
                #         if path[-1] == prop.identifier:
                #             in_search_prop = True
                #             node.search_value = prop.name
                #             bpy.ops.scripting_nodes.add_scene_data_socket(node_name=node.name, socket_name=prop.name, is_output=False, use_four_numbers=node.search_properties[prop.name].use_four_numbers, is_color=node.search_properties[prop.name].is_color)
                #             node.inputs[2].set_value(eval(value))

                #     if not in_search_prop:
                #         try:
                #             if type(eval(value)) == str:
                #                 bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="STRING")
                #                 node.inputs[2].set_value(eval(value))
                #             elif type(eval(value)) == bool:
                #                 bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="BOOLEAN")
                #                 node.inputs[2].set_value(eval(value))
                #             elif type(eval(value)) == int:
                #                 bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="INTEGER")
                #                 node.inputs[2].set_value(eval(value))
                #             elif type(eval(value)) == float:
                #                 bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="FLOAT")
                #                 node.inputs[2].set_value(eval(value))
                #             elif type(eval(value)) == tuple:
                #                 bpy.ops.scripting_nodes.add_custom_socket(node_name=node.name, propName=path[-1], is_output=False, propType="VECTOR")
                #                 node.inputs[2].set_value(eval(value))
                #         except:
                #             pass



    recording_action: bpy.props.BoolProperty(default=False,name="Record Actions",update=update_record_action)
