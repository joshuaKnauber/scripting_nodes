import bpy
import textwrap



def draw_section(context, layout, text):
    indents = 0
    for section in text.split("\n"):
        col = layout.column(align=True)
        indents = 0
        for line in textwrap.wrap(section, context.scene.sn.line_length):
            if line[0] == "-":
                indents = 0
            col.label(text=indents*" " + line)
            if line[0] == "-":
                indents = 3



class SN_PT_NodeDocsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_NodeDocs"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Node"
    bl_order = 1
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree and context.space_data.node_tree.nodes.active

    def draw_header(self, context):
        layout = self.layout
        layout.label(text=context.space_data.node_tree.nodes.active.name + " Documentation")
        layout.prop(context.scene.sn, "show_wrap_settings", text="", icon_only=True, emboss=False, icon="PREFERENCES")

    def draw(self, context):
        layout = self.layout
        node = context.space_data.node_tree.nodes.active
        
        if context.scene.sn.show_wrap_settings:
            layout.prop(context.scene.sn, "line_length")
            layout.separator()
        
        if "description" in node.docs and node.docs["description"]:
            draw_section(context, layout, node.docs["description"])
        else:
            layout.label(text=f"{node.name} is undocumented")



class SN_PT_NodeSettingsPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_NodeDocs"
    bl_idname = "SN_PT_NodeSettingsPanel"
    bl_label = "Settings"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Node"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree and context.space_data.node_tree.nodes.active:
            node = context.space_data.node_tree.nodes.active
            return "settings" in node.docs and node.docs["settings"]

    def draw(self, context):
        layout = self.layout
        node = context.space_data.node_tree.nodes.active
        if "settings" in node.docs and node.docs["settings"]:
            draw_section(context, layout, node.docs["settings"])



class SN_PT_NodeInputsPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_NodeDocs"
    bl_idname = "SN_PT_NodeInputsPanel"
    bl_label = "Inputs"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Node"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree and context.space_data.node_tree.nodes.active:
            node = context.space_data.node_tree.nodes.active
            return "inputs" in node.docs and node.docs["inputs"]

    def draw(self, context):
        layout = self.layout
        node = context.space_data.node_tree.nodes.active
        if "inputs" in node.docs and node.docs["inputs"]:
            draw_section(context, layout, node.docs["inputs"])



class SN_PT_NodeOutputsPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_NodeDocs"
    bl_idname = "SN_PT_NodeOutputsPanel"
    bl_label = "Outputs"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Node"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree and context.space_data.node_tree.nodes.active:
            node = context.space_data.node_tree.nodes.active
            return "outputs" in node.docs and node.docs["outputs"]

    def draw(self, context):
        layout = self.layout
        node = context.space_data.node_tree.nodes.active
        if "outputs" in node.docs and node.docs["outputs"]:
            draw_section(context, layout, node.docs["outputs"])