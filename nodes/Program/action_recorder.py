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
        context.space_data.node_tree.set_changes(True)
        return {"FINISHED"}


class SN_OT_ExportToOperator(bpy.types.Operator):
    bl_idname = "sn.export_to_operator"
    bl_label = "Export to Run Operator node"
    bl_description = "Exports to a run operator node"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    operator_string: bpy.props.StringProperty()

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_RunOperatorNode",use_transform=True)
        graph_tree.nodes.active.use_internal = True
        graph_tree.nodes.active.operator = self.operator_string
        return {"FINISHED"}


class SN_OT_RunActions(bpy.types.Operator):
    bl_idname = "sn.run_actions"
    bl_label = "Run the recorded actions"
    bl_description = "Runs the recorded actions of this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        try:
            for action in node.actions:
                exec(action.identifier)
        except:
            self.report({"ERROR"},message="Failed to run! This button might not work for all cases.")
        return {"FINISHED"}


class SN_RecorderNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RecorderNode"
    bl_label = "Action Recorder"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "always_recompile": True
    }

    actions: bpy.props.CollectionProperty(type=SN_GenericPropertyGroup)


    def on_create(self,context):
        self.add_execute_input("Action Recorder")
        self.add_execute_output("Execute").mirror_name = True

    def draw_node(self,context,layout):
        if self.actions:
            actions = ""
            for action in self.actions:
                actions += action.identifier + "\n"
            split = layout.split(factor=0.6, align=True)
            if not self.recording_action:
                split.prop(self, "recording_action", text="Start Recording", toggle=True, icon="RADIOBUT_OFF")
                split.operator("sn.get_python_name", text="Copy all",icon="COPYDOWN").to_copy = actions
            else:
                split.prop(self, "recording_action", text="Stop Recording", toggle=True, icon="RADIOBUT_ON")
                split.operator("sn.get_python_name", text="Copy all",icon="COPYDOWN").to_copy = actions

            row = layout.row()
            row.scale_y = 1.4
            row.operator("sn.run_actions",text="Run Actions",icon="PLAY").node = self.name

        else:
            if not self.recording_action:
                layout.prop(self, "recording_action", text="Start Recording", toggle=True, icon="RADIOBUT_OFF")
            else:
                layout.prop(self, "recording_action", text="Stop Recording", toggle=True, icon="RADIOBUT_ON")


        if len(self.actions):
            box = layout.box()
            for x, action in enumerate(self.actions):
                row = box.row(align=True)

                op = row.operator("sn.question_mark", text="", icon="QUESTION", emboss=False)
                op.to_display = action.identifier
                op.allow_copy = True
                row.label(text=action.name)

                if "bpy.ops" in action.identifier:
                    row.operator("sn.export_to_operator", text="", icon="EXPORT", emboss=False).operator_string = action.identifier

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
                    new_action = self.actions.add()
                    if "bpy.ops." in action:
                        name = action.split("(")[0].split(".")
                        new_action.name = name[-2].replace("_", " ").title() + " - " + eval(action.split("(")[0] + ".get_rna_type().name")
                        new_action.description = action
                        new_action.identifier = action

                    elif "bpy.data" in action:
                        new_action.name = action.replace("bpy.data.", "").replace(".", " -> ").replace("_", " ").title()
                        new_action.description = action
                        new_action.identifier = action

                    elif "bpy.context" in action:
                        new_action.name = action.replace("bpy.context.", "").replace(".", " -> ").replace("_", " ").title()
                        new_action.description = action
                        new_action.identifier = action


    recording_action: bpy.props.BoolProperty(default=False,name="Record Actions",update=update_record_action)


    def code_evaluate(self, context, touched_socket):
        actions = []
        for action in self.actions:
            actions.append(action.identifier + "\n")

        return {
            "code": f"""
                    {self.list_code(actions, 5)}
                    {self.outputs[0].code(5)}
                    """
        }