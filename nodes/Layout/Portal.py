import bpy
from random import uniform
from ..base_node import SN_ScriptingBaseNode



class SN_PortalNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_PortalNode"
    bl_label = "Portal"
    bl_width_default = 100
    
    def update_connected_portals(self, context=None):
        if self.direction == "INPUT":
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for node in ntree.node_collection(self.bl_idname).nodes:
                        if node.direction == "OUTPUT" and node.var_name == self.var_name:
                            node.var_name = self.var_name

    def update_direction(self, context):
        self.inputs[0].set_hide(self.direction == "OUTPUT")
        self.outputs[0].set_hide(self.direction == "INPUT")
        self._evaluate(context)
    
    direction: bpy.props.EnumProperty(name="Direction",
                                description="The direction this portal goes in",
                                items=[("INPUT", "In", "Input", "BACK", 0),
                                       ("OUTPUT", "Out", "Output", "FORWARD", 1)],
                                update=update_direction)

    def update_var_name(self, context):
        self.label = self.var_name
        self._evaluate(context)

    def get_var_name(self):
        return self.get("_var_name", "")

    def set_var_name(self, value):
        if self.direction == "INPUT":
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for node in ntree.node_collection(self.bl_idname).nodes:
                        if node.direction == "OUTPUT" and node.var_name == self.var_name:
                            node["_var_name"] = value
        self["_var_name"] = value
    
    var_name: bpy.props.StringProperty(name="Name",
                                description="The identifier that links this portal to another portal",
                                get=get_var_name, set=set_var_name,
                                update=update_var_name)
    
    def update_custom_color(self, context):
        # update own color
        self.color = self.custom_color
        # update connected color
        if self.direction == "INPUT":
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for node in ntree.node_collection(self.bl_idname).nodes:
                        if node.direction == "OUTPUT" and node.var_name == self.var_name:
                            node.custom_color = self.custom_color
    
    custom_color: bpy.props.FloatVectorProperty(name="Color",
                                size=3, min=0, max=1, subtype="COLOR",
                                description="The color of this node",
                                update=update_custom_color)

    def on_create(self, context):
        self.add_data_input()
        out = self.add_data_output()
        out.changeable = True
        out.set_hide(True)
        self.var_name = self.uuid
        self.custom_color = (uniform(0,1), uniform(0,1), uniform(0,1))

    def evaluate(self, context):
        if self.direction == "INPUT":
            self.update_connected_portals()
        elif self.direction == "OUTPUT":
            for ntree in bpy.data.node_groups:
                if ntree.bl_idname == "ScriptingNodesTree":
                    for node in ntree.node_collection(self.bl_idname).nodes:
                        if node.direction == "INPUT" and node.var_name == self.var_name:
                            self.outputs[0].python_value = node.inputs[0].python_value
                            return
            self.outputs[0].reset_value()
    
    def draw_node(self, context, layout):
        layout.prop(self, "direction", expand=True)
        if self.direction == "INPUT":
            row = layout.row(align=True)
            split = row.split(factor=0.6, align=True)
            split.prop(self, "var_name", text="")
            sub_split = split.split(factor=0.5, align=True)
            sub_split.prop(self, "custom_color", text="")
            sub_split.operator("sn.reset_portal", text="", icon="LOOP_BACK").node = self.name