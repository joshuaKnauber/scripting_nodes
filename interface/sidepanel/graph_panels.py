import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_OT_GetPythonName(bpy.types.Operator):
    bl_idname = "sn.get_python_name"
    bl_label = "Get Python Name"
    bl_description = "Get the python name for this element"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    to_copy: bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.window_manager.clipboard = self.to_copy
        self.report({"INFO"},message="Python path copied")
        return {"FINISHED"}


class SN_OT_QuestionMarkName(bpy.types.Operator):
    bl_idname = "sn.question_mark"
    bl_label = "Questionmark"
    bl_description = "Explanation to what this is"
    bl_options = {"REGISTER","INTERNAL"}
    
    to_display: bpy.props.StringProperty()
    allow_copy: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        return {"FINISHED"}

    def draw(self,context):
        if "\n" in self.to_display:
            col = self.layout.column(align=True)
            for line in self.to_display.split("\n"):
                col.label(text=line)
        else:
            row = self.layout.row(align=True)
            if self.allow_copy:
                row.operator("sn.get_python_name", text="",icon="COPYDOWN", emboss=False).to_copy = self.to_display
            row.label(text=self.to_display)

    def invoke(self, context, event):
        if "\n" in self.to_display:
            longest_text = ""
            for line in self.to_display.split("\n"):
                if len(line) > len(longest_text):
                    longest_text = line

            return context.window_manager.invoke_popup(self, width=len(longest_text)*6)
        else:
            return context.window_manager.invoke_popup(self, width=len(self.to_display)*6)


class SN_PT_GraphPanel(bpy.types.Panel):
    bl_idname = "SN_PT_GraphPanel"
    bl_label = "Graphs"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree"

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        row = layout.row(align=False)
        row.template_list("SN_UL_GraphList", "Graphs", bpy.data, "node_groups", sn, "node_tree_index", rows=4)
        col = row.column(align=True)
        col.operator("node.new_node_tree", text="", icon="ADD")
        col.operator("sn.append_graph", text="", icon="APPEND_BLEND")
        col.operator("sn.remove_graph", text="", icon="REMOVE").index = sn.node_tree_index



class SN_PT_VariablePanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_VariablePanel"
    bl_label = "Variables"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 1

    def draw(self, context):
        layout = self.layout



class SN_PT_PropertyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PropertyPanel"
    bl_label = "Properties"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 1
    
    def draw(self, context):
        layout = self.layout
            
            

class SN_PT_AssetsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AssetsPanel"
    bl_label = "Assets"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 2
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout



class SN_PT_IconPanel(bpy.types.Panel):
    bl_idname = "SN_PT_IconPanel"
    bl_label = "Custom Icons"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 3
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout



class SN_PT_AddonInfoPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_label = "Addon"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree"

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(sn, "addon_name")
        layout.prop(sn, "description")
        layout.prop(sn, "author")
        layout.prop(sn, "location")
        layout.prop(sn, "warning")
        layout.prop(sn, "doc_url")
        layout.prop(sn, "tracker_url")
        col = layout.column(align=True)
        col.prop(sn, "category")
        if sn.category == "CUSTOM":
            col.prop(sn, "custom_category", text=" ")
        layout.prop(sn, "version")
        layout.prop(sn, "blender")
        
        row = layout.row()
        row.scale_y = 1.5
        col = row.column(align=True)
        col.operator("sn.save_addon",text="Save Addon",icon="FILE_TICK")
        row = col.row()
        row.scale_y = 0.7
        row.operator("sn.export_to_marketplace",text="Add to Marketplace",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id)



class SN_PT_SnippetPanel(bpy.types.Panel):
    bl_idname = "SN_PT_SnippetPanel"
    bl_label = "Snippets"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 5
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout



class SN_PT_AddonSettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonSettingsPanel"
    bl_label = "Settings"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 6

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree"

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        addon_graph = addon_tree.sn_graphs[0]

        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row()
        row.alignment = "RIGHT"
        row.label(text="Last Compile: "+addon_graph.last_compile_time)

        layout.prop(addon_graph, "compile_on_start", text="Compile on Startup")

        layout.separator()

        layout.prop(addon_graph, "autocompile", text="Auto Compile")
        row = layout.row()
        row.enabled = addon_graph.autocompile
        row.prop(addon_graph, "autocompile_delay", text="Delay")

        layout.separator()

        col = layout.column()
        col.enabled = bpy.data.is_saved
        col.prop(context.scene.sn, "use_autosave")
        row = col.row()
        row.enabled = context.scene.sn.use_autosave
        row.prop(context.scene.sn, "autosave_delay")

        layout.separator()

        layout.template_ID(context.scene.sn, "easy_bpy",
                           open="text.open", text="Easy BPY")



def draw_property(context,var,layout,from_node="",node_attr="",node_index=0):
    col = layout.column()
    col.use_property_split = True
    col.use_property_decorate = False
    
    row = col.row(align=True)
    row.prop(var,"var_type",text="Type")
    copy_name = var.attach_property_to.upper() + "_PLACEHOLDER." + var.identifier
    if var.use_self:
        if "pref" in from_node.lower():
            copy_name = f"bpy.context.preferences.addons['{context.scene.sn.addon_tree().sn_graphs[0].short()}'].preferences.{var.identifier}"
        else:
            copy_name = "self." + var.identifier
    row.operator("sn.get_python_name",text="",icon="COPYDOWN").to_copy = copy_name
    col.separator()

    if not var.use_self:
        col.prop(var,"attach_property_to",text="Attach To")
        col.separator()

    if var.property_subtype != "NO_SUBTYPES":
        col.prop(var,"property_subtype",text="Subtype")
        col.separator()
    if var.property_unit != "NO_UNITS":
        col.prop(var,"property_unit",text="Unit")
        col.separator()

    if var.var_type in ["BOOLEAN","FLOAT","INTEGER"]:
        col.prop(var,"is_vector")
        if var.is_vector:
            col.prop(var,"vector_size")
        col.separator()

    col.row(align=True).prop(var, "property_options")
    col.prop(var,"description")
    col.separator()
    
    if var.var_type == "STRING":
        col.prop(var,"str_default")
        
    elif var.var_type == "INTEGER":
        if not var.is_vector:
            col.prop(var,"int_default")
        elif var.vector_size == 2:
            col.prop(var,"int_two_default")
        elif var.vector_size == 3:
            col.prop(var,"int_three_default")
        elif var.vector_size == 4:
            col.prop(var,"int_four_default")
        
        col.separator()
        
        sub_row = col.row()
        sub_row.prop(var,"use_min",text="")
        sub_col = sub_row.column()
        sub_col.enabled = var.use_min
        sub_col.prop(var,"int_min")
        
        sub_row = col.row()
        sub_row.prop(var,"use_max",text="")
        sub_col = sub_row.column()
        sub_col.enabled = var.use_max
        sub_col.prop(var,"int_max")
        
        sub_row = col.row()
        sub_row.prop(var,"use_soft_min",text="")
        sub_col = sub_row.column()
        sub_col.enabled = var.use_soft_min
        sub_col.prop(var,"int_soft_min")
        
        sub_row = col.row()
        sub_row.prop(var,"use_soft_max",text="")
        sub_col = sub_row.column()
        sub_col.enabled = var.use_soft_max
        sub_col.prop(var,"int_soft_max")
            
    elif var.var_type == "FLOAT":
        if not var.is_vector:
            col.prop(var,"float_default")
        elif var.vector_size == 2:
            col.prop(var,"float_two_default")
        elif var.vector_size == 3:
            col.prop(var,"float_three_default")
        elif var.vector_size == 4:
            col.prop(var,"float_four_default")

        col.prop(var,"float_precision")
        
        col.separator()
        
        sub_row = col.row()
        sub_row.prop(var,"use_min",text="")
        sub_col = sub_row.column()
        sub_col.enabled = var.use_min
        sub_col.prop(var,"float_min")
        
        sub_row = col.row()
        sub_row.prop(var,"use_max",text="")
        sub_col = sub_row.column()
        sub_col.enabled = var.use_max
        sub_col.prop(var,"float_max")
        
        sub_row = col.row()
        sub_row.prop(var,"use_soft_min",text="")
        sub_col = sub_row.column()
        sub_col.enabled = var.use_soft_min
        sub_col.prop(var,"float_soft_min")
        
        sub_row = col.row()
        sub_row.prop(var,"use_soft_max",text="")
        sub_col = sub_row.column()
        sub_col.enabled = var.use_soft_max
        sub_col.prop(var,"float_soft_max")
        
    elif var.var_type == "BOOLEAN":
        if not var.is_vector:
            col.prop(var,"bool_default",toggle=True)
        elif var.vector_size == 2:
            column = col.column(align=True)
            for i in range(2):
                column.prop(var,"bool_two_default",toggle=True,text=str(var.bool_two_default[i]),index=i)
        elif var.vector_size == 3:
            column = col.column(align=True)
            for i in range(3):
                column.prop(var,"bool_three_default",toggle=True,text=str(var.bool_three_default[i]),index=i)
        elif var.vector_size == 4:
            column = col.column(align=True)
            for i in range(4):
                column.prop(var,"bool_four_default",toggle=True,text=str(var.bool_four_default[i]),index=i)

    elif var.var_type == "ENUM":
        # col.prop(var,"dynamic_enum")
        # col.separator()
        
        if not var.dynamic_enum:
            for index, item in enumerate(var.enum_items):
                box = col.box()
                header_row = box.row(align=True)
                header_row.prop(item,"name",text="")
                op = header_row.operator("sn.move_enum_item",text="",icon="TRIA_UP")
                op.index = index
                op.down = False
                op.node = from_node
                op.node_attr = node_attr
                op.node_index = node_index
                op = header_row.operator("sn.move_enum_item",text="",icon="TRIA_DOWN")
                op.index = index
                op.down = True
                op.node = from_node
                op.node_attr = node_attr
                op.node_index = node_index
                op = header_row.operator("sn.remove_enum_item",text="",icon="PANEL_CLOSE")
                op.index = index
                op.node = from_node
                op.node_attr = node_attr
                op.node_index = node_index
                box.prop(item,"description")
                
            op = col.operator("sn.add_enum_item",text="Add Enum Item", icon="ADD")
            op.node = from_node
            op.node_attr = node_attr
            op.node_index = node_index


"""

            
            

"""