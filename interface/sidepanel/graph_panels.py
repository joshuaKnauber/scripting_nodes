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

        addon_tree = context.scene.sn.addon_tree()

        row = layout.row(align=False)
        row.template_list("SN_UL_GraphList", "Graphs", addon_tree, "sn_graphs", addon_tree, "sn_graph_index",rows=3)
        col = row.column(align=True)
        col.operator("sn.add_graph", text="", icon="ADD")
        col.operator("sn.append_graph", text="", icon="APPEND_BLEND")
        col.operator("sn.remove_graph", text="", icon="REMOVE").index = addon_tree.sn_graph_index


bpy.utils.register_class(SN_PT_GraphPanel)


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

        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        row = layout.row(align=False)
        col = row.column(align=True)
        col.template_list("SN_UL_VariableList", "Variables", graph_tree, "sn_variables", graph_tree, "sn_variable_index",rows=3)
        if len(graph_tree.sn_variables):
            var = graph_tree.sn_variables[graph_tree.sn_variable_index]
            btn_row = col.row(align=True)
            btn_row.operator("sn.add_var_getter",icon="SORT_DESC", text="Getter")
            btn_row.operator("sn.add_var_setter",icon="SORT_ASC", text="Setter")
            copy_name = f"{SN_ScriptingBaseNode().get_python_name(graph_tree.name)}[\"{var.identifier}\"]"
            btn_row.operator("sn.get_python_name",text="",icon="UV_SYNC_SELECT").to_copy = copy_name
        col = row.column(align=True)
        col.operator("sn.add_variable", text="", icon="ADD")
        col.operator("sn.remove_variable", text="", icon="REMOVE")
        
        if len(graph_tree.sn_variables):
            layout.separator()
            row = layout.row()
            col = row.column()
            col.use_property_split = True
            col.use_property_decorate = False
            
            col.prop(var,"var_type",text="Type")
            col.separator()
            
            if var.var_type == "STRING":
                col.prop(var,"str_default")
            elif var.var_type == "INTEGER":
                col.prop(var,"int_default")
            elif var.var_type == "FLOAT":
                col.prop(var,"float_default")
            elif var.var_type == "BOOLEAN":
                col.prop(var,"bool_default")
            elif var.var_type == "LIST":
                col.label(text="There are no defaults for lists.", icon="QUESTION")
            elif var.var_type == "BLEND_DATA":
                col.prop(var,"is_data_collection")

            
            row.label(text="",icon="BLANK1")


def draw_property(context,var,layout,from_node="",node_attr="",node_index=0):
    col = layout.column()
    col.use_property_split = True
    col.use_property_decorate = False
    
    row = col.row(align=True)
    row.prop(var,"var_type",text="Type")
    copy_name = var.attach_property_to.upper() + "." + var.identifier
    if var.use_self: copy_name = "self." + var.identifier
    row.operator("sn.get_python_name",text="",icon="UV_SYNC_SELECT").to_copy = copy_name
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

    col.prop(var,"description")
    col.separator()
    
    if var.var_type == "STRING":
        col.prop(var,"str_default")
        
    elif var.var_type == "INTEGER":
        if not var.is_vector:
            col.prop(var,"int_default")
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
        elif var.vector_size == 3:
            col.prop(var,"float_three_default")
        elif var.vector_size == 4:
            col.prop(var,"float_four_default")
        
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
        elif var.vector_size == 3:
            column = col.column(align=True)
            for i in range(3):
                column.prop(var,"bool_three_default",toggle=True,text=str(var.bool_three_default[i]),index=i)
        elif var.vector_size == 4:
            column = col.column(align=True)
            for i in range(4):
                column.prop(var,"bool_four_default",toggle=True,text=str(var.bool_four_default[i]),index=i)

    elif var.var_type == "ENUM":
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
            op.node = from_node
            op.node_attr = node_attr
            op.node_index = node_index
            box.prop(item,"description")
        op = col.operator("sn.add_enum_item",text="Add Enum Item", icon="ADD")
        op.node = from_node
        op.node_attr = node_attr
        op.node_index = node_index
            
            
class SN_PT_PropertyPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_PropertyPanel"
    bl_label = "Properties"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 2
    

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()

        row = layout.row(align=False)
        col = row.column(align=True)
        col.template_list("SN_UL_VariableList", "Properties", addon_tree, "sn_properties", addon_tree, "sn_property_index",rows=3)
        if len(addon_tree.sn_properties):
            btn_row = col.row(align=True)
            btn_row.operator("sn.add_prop_getter",icon="SORT_DESC", text="Getter")
            btn_row.operator("sn.add_prop_setter",icon="SORT_ASC", text="Setter")
        col = row.column(align=True)
        col.operator("sn.add_property", text="", icon="ADD")
        col.operator("sn.remove_property", text="", icon="REMOVE")
        
        if len(addon_tree.sn_properties):
            layout.separator()
            row = layout.row()
            draw_property(context, addon_tree.sn_properties[addon_tree.sn_property_index], row)
            row.label(text="",icon="BLANK1")


class SN_PT_IconPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_IconPanel"
    bl_label = "Custom Icons"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 3
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        
        row = layout.row(align=False)
        col = row.column(align=True)
        col.template_list("SN_UL_IconList", "Custom Icons", addon_tree, "sn_icons", addon_tree, "sn_icon_index",rows=3)
        if len(addon_tree.sn_icons):
            col.operator("sn.add_get_icon",icon="SORT_DESC", text="Getter")
        col = row.column(align=True)
        col.operator("sn.add_icon", text="", icon="ADD")
        col.operator("sn.remove_icon", text="", icon="REMOVE")
        
        
        if len(addon_tree.sn_icons):
            col = layout.column()
            row = col.row()
            icon = addon_tree.sn_icons[addon_tree.sn_icon_index]
            row.template_ID(icon, "image", new="image.new", open="image.open")
            row.label(icon="BLANK1")
            
            
class SN_PT_AssetsPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_AssetsPanel"
    bl_label = "Assets"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 4
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        
        row = layout.row(align=False)
        col = row.column(align=True)
        col.template_list("SN_UL_AssetList", "Assets", addon_tree, "sn_assets", addon_tree, "sn_asset_index",rows=3)
        if len(addon_tree.sn_assets) and addon_tree.sn_assets[addon_tree.sn_asset_index].name:
            col.operator("sn.add_get_asset",icon="SORT_DESC", text="Getter")
        col = row.column(align=True)
        col.operator("sn.add_asset", text="", icon="ADD")
        col.operator("sn.remove_asset", text="", icon="REMOVE")
        
        
        if len(addon_tree.sn_assets):
            col = layout.column()
            row = col.row()
            row.prop(addon_tree.sn_assets[addon_tree.sn_asset_index],"path",text="")
            row.label(icon="BLANK1")
        
        
            
            
            
bpy.utils.register_class(SN_PT_VariablePanel)
bpy.utils.register_class(SN_PT_PropertyPanel)
bpy.utils.register_class(SN_PT_IconPanel)
bpy.utils.register_class(SN_PT_AssetsPanel)