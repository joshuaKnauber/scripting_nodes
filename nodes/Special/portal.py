import bpy
from random import randint
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



from_portal = None



class SN_GetPortalReceiver(bpy.types.Operator):
    bl_idname = "sn.get_portal"
    bl_label = "Get Portal Receiver"
    bl_description = "Gives you a portal receiver node belonging to this portal"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty()

    def execute(self, context):
        global from_portal
        from_portal = context.space_data.node_tree.nodes[self.node]
        bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_OutPortalNode",use_transform=True)
        return {"FINISHED"}



class SN_DuplicatePortalReceiver(bpy.types.Operator):
    bl_idname = "sn.duplicate_portal"
    bl_label = "Duplicate Portal Receiver"
    bl_description = "Gives you another portal receiver node for this portal"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty()

    def execute(self, context):
        for node in context.space_data.node_tree.nodes:
            node.select = node.name == self.node
        bpy.ops.node.duplicate_move("INVOKE_DEFAULT")
        return {"FINISHED"}



class SN_FindPortal(bpy.types.Operator):
    bl_idname = "sn.find_portal"
    bl_label = "Find Portal"
    bl_description = "Finds the portal this node belongs to"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    color: bpy.props.FloatVectorProperty(size=3,min=0,max=1,subtype="COLOR")
    loc: bpy.props.FloatVectorProperty(size=2)

    def execute(self, context):
        found = False
        for node in context.space_data.node_tree.nodes:
            node.select = node.bl_idname == "SN_InPortalNode" and node.color == self.color
            if not found: found = node.bl_idname == "SN_InPortalNode" and node.color == self.color
        
        if found:
            bpy.ops.node.view_selected("INVOKE_DEFAULT")
        else:
            self.report({"WARNING"},message="No origin portal found for the receiver! Added new origin node.")
            origin = context.space_data.node_tree.nodes.new("SN_InPortalNode")
            origin.color = self.color
            origin.location = ( self.loc[0]-100, self.loc[1] )
        return {"FINISHED"}



class SN_SelectPortals(bpy.types.Operator):
    bl_idname = "sn.select_portals"
    bl_label = "Select Portals"
    bl_description = "Finds the portals this node transfers data to"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    color: bpy.props.FloatVectorProperty(size=3,min=0,max=1,subtype="COLOR")

    def execute(self, context):
        found = False
        for node in context.space_data.node_tree.nodes:
            node.select = node.bl_idname == "SN_OutPortalNode" and node.color == self.color
            if not found: found = node.bl_idname == "SN_OutPortalNode" and node.color == self.color
        
        if not found:
            self.report({"INFO"},message="No receiving portals found.")

        return {"FINISHED"}



class SN_InPortalNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InPortalNode"
    bl_label = "Portal"
    # bl_icon = "GRAPH"
    bl_width_default = 75

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def setup_new(self):
        self.color = ( randint(0,1000)/1000, randint(0,1000)/1000, randint(0,1000)/1000 )


    def on_create(self,context):
        self.label = "In"
        self.add_data_input("Value")
        self.setup_new()


    def on_copy(self,node):
        self.setup_new()


    def draw_node(self,context,layout):
        row = layout.row()
        col = row.column()
        col.scale_x = 2
        col.operator("sn.get_portal",text="",icon="PASTEDOWN").node = self.name
        row.operator("sn.select_portals",text="",icon="RESTRICT_SELECT_OFF",emboss=False).color = self.color


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"{self.inputs[0].code()}"
        }



class SN_OutPortalNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OutPortalNode"
    bl_label = "Portal"
    # bl_icon = "GRAPH"
    bl_width_default = 75

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.label = "Out"
        self.add_data_output("Value")
        if from_portal:
            self.color = from_portal.color


    def draw_node(self,context,layout):
        row = layout.row()
        col = row.column()
        col.scale_x = 2
        col.operator("sn.duplicate_portal",text="",icon="DUPLICATE").node = self.name
        op = row.operator("sn.find_portal",text="",icon="RESTRICT_SELECT_OFF",emboss=False)
        op.color = self.color
        op.loc = self.location


    def code_evaluate(self, context, touched_socket):

        for node in self.node_tree.nodes:
            if node.bl_idname == "SN_InPortalNode" and node.color == self.color:

                return {
                    "code": f"{node.inputs[0].code()}"
                }

        return {
            "code": f"None"
        }