import bpy
from random import uniform
from ..base_node import SN_ScriptingBaseNode



class SN_TimestampNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_TimestampNode"
    bl_label = "Timestamp"
    bl_width_default = 200
    
    def update_connected_portals(self, context=None):
        if self.timestamp_type == "START":
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for node in ntree.node_collection(self.bl_idname).nodes:
                        if node.timestamp_type == "END" and node.var_name == self.var_name:
                            node.var_name = self.var_name
    
    timestamp_type: bpy.props.EnumProperty(name="Type",
                                description="Start the timestamp recording or print the total time since the start",
                                items=[("START", "Start", "Start", "MOD_TIME", 0),
                                       ("END", "End", "End", "TIME", 1)],
                                update=update_connected_portals)

    timestamp: bpy.props.FloatProperty(name="Timestamp")

    def update_var_name(self, context):
        self.label = self.var_name
        self._evaluate(context)

    def get_var_name(self):
        return self.get("_var_name", "")

    def set_var_name(self, value):
        if self.timestamp_type == "INPUT":
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for node in ntree.node_collection(self.bl_idname).nodes:
                        if node.timestamp_type == "OUTPUT" and node.var_name == self.var_name:
                            node["_var_name"] = value
        self["_var_name"] = value
    
    var_name: bpy.props.StringProperty(name="Name",
                                description="The identifier that links this timestamp to other timestamps",
                                get=get_var_name, set=set_var_name,
                                update=update_var_name)
    
    def update_custom_color(self, context):
        # update own color
        self.color = self.custom_color
        # update connected color
        if self.timestamp_type == "START":
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for node in ntree.node_collection(self.bl_idname).nodes:
                        if node.timestamp_type == "END" and node.var_name == self.var_name:
                            node.custom_color = self.custom_color
    
    custom_color: bpy.props.FloatVectorProperty(name="Color",
                                size=3, min=0, max=1, subtype="COLOR",
                                description="The color of this node",
                                update=update_custom_color)

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.var_name = self.uuid
        self.custom_color = (uniform(0,1), uniform(0,1), uniform(0,1))

    def evaluate(self, context):
        self.code_import = "import time"
        if self.timestamp_type == "START":
            self.code = f"""
            t_{self.var_name} = time.time()
            {self.indent(self.outputs[0].python_value, 3)}
            """
        elif self.timestamp_type == "END":
            self.code = f"""
            if "t_{self.var_name}" in locals(): print(f"Time elapsed for {self.var_name}: {{(time.time() - t_{self.var_name}) * 1000}}ms")
            try: bpy.data.node_groups['{self.node_tree.name}'].nodes['{self.name}'].timestamp = time.time() - t_{self.var_name}
            except: print("Failed to set timestamp on node")
            for a in bpy.context.screen.areas: a.tag_redraw()
            {self.indent(self.outputs[0].python_value, 3)}
            """

    def evaluate_export(self, context):
        self.code = f"""
            {self.indent(self.outputs[0].python_value, 3)}
            """
    
    def draw_node(self, context, layout):
        layout.prop(self, "timestamp_type", expand=True)
        if self.timestamp_type == "START":
            row = layout.row(align=True)
            split = row.split(factor=0.6, align=True)
            split.prop(self, "var_name", text="")
            sub_split = split.split(factor=0.5, align=True)
            sub_split.prop(self, "custom_color", text="")
            sub_split.operator("sn.reset_portal", text="", icon="LOOP_BACK").node = self.name
        else:
            layout.label(text=f"Time elapsed: {self.timestamp*1000}ms")