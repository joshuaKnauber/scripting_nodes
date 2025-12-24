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
        # If switched to output, try to match the color of the target
        if self.direction == "OUTPUT":
            self.update_var_name(context)
        else:
            self._evaluate(context)
    
    direction: bpy.props.EnumProperty(name="Direction",
                                description="The direction this portal goes in",
                                items=[("INPUT", "In", "Input", "BACK", 0),
                                       ("OUTPUT", "Out", "Output", "FORWARD", 1)],
                                update=update_direction)

    def sync_portals(self):
        try:
            prev = self.get("_prev_var_name", self.var_name)
            
            # If we are an INPUT, update our children's names
            if self.direction == "INPUT" and prev != self.var_name:
                for ntree in bpy.data.node_groups:
                    if ntree.bl_idname == "ScriptingNodesTree":
                        coll = ntree.node_collection(self.bl_idname)
                        for other in coll.nodes:
                            if other and other.direction == "OUTPUT" and other.var_name == prev:
                                other.var_name = self.var_name
                                other.label = self.var_name

            # If we are an OUTPUT, match the color of our target
            elif self.direction == "OUTPUT":
                for ntree in bpy.data.node_groups:
                    if ntree.bl_idname == "ScriptingNodesTree":
                        coll = ntree.node_collection(self.bl_idname)
                        for other in coll.nodes:
                            if other and other.direction == "INPUT" and other.var_name == self.var_name:
                                self.custom_color = other.custom_color
                                break
            
            self["_prev_var_name"] = self.var_name
        except:
            pass

    def update_var_name(self, context=None):
        self.label = self.var_name
        self.sync_portals()
        self._evaluate(context)

    var_name: bpy.props.StringProperty(
        name="Name",
        description="The identifier that links this portal to another portal",
        update=update_var_name,
    )
    
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
        # Only assign a new UUID if we don't have a name (e.g. fresh node vs duplicated node)
        if not self.var_name:
            self.var_name = self.uuid
        self["_prev_var_name"] = self.var_name
        self.label = self.var_name
        self.custom_color = (uniform(0, 1), uniform(0, 1), uniform(0, 1))

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
        # Safeguard for Blender 5.0 reloads: if label is blank, restore it
        if not self.label:
            self.label = self.var_name

        layout.prop(self, "direction", expand=True)
        
        row = layout.row(align=True)
        split = row.split(factor=0.6, align=True)
        split.prop(self, "var_name", text="")
        sub_split = split.split(factor=0.5, align=True)
        sub_split.prop(self, "custom_color", text="")
        sub_split.operator("sn.reset_portal", text="", icon="LOOP_BACK").node = self.name