import bpy
from bpy import props
from .base_socket import ScriptingSocket


class SN_OT_SetIcon(bpy.types.Operator):
    bl_idname = "sn.set_icon"
    bl_label = "Set Icon"
    bl_description = "Sets this icon"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    node: bpy.props.StringProperty()
    socket: bpy.props.IntProperty()
    icon: bpy.props.IntProperty()

    def execute(self, context):
        if self.socket != -1:
            context.space_data.node_tree.nodes[self.node].inputs[self.socket].default_value = self.icon
        else:
            context.space_data.node_tree.nodes[self.node].icon = self.icon
        context.area.tag_redraw()
        return {"FINISHED"}


class SN_OT_SelectIcon(bpy.types.Operator):
    bl_idname = "sn.select_icon"
    bl_label = "Select Icon"
    bl_description = "Shows you a selection of all blender icons"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    bl_property = "icon_search"
    
    node: bpy.props.StringProperty()
    socket: bpy.props.IntProperty()
    icon_search: bpy.props.StringProperty(name="Search", options={"SKIP_SAVE"})

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self,context,event):
        return context.window_manager.invoke_popup(self, width=800)

    def draw(self,context):
        layout = self.layout
        icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
        if self.socket != -1:
            prop = context.space_data.node_tree.nodes[self.node].inputs[self.socket].default_value
        else:
            prop = context.space_data.node_tree.nodes[self.node].icon

        row = layout.row()
        row.prop(self,"icon_search",text="",icon="VIEWZOOM")

        grid = layout.grid_flow(align=True,even_columns=True, even_rows=True)
        for icon in icons:
            if self.icon_search.lower() in icon.name.lower() or not self.icon_search:
                op = grid.operator("sn.set_icon",text="", icon_value=icon.value, emboss=prop==icon.value)
                op.node = self.node
                op.socket = self.socket
                op.icon = icon.value


class SN_IconSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_IconSocket"
    group = "DATA"
    bl_label = "Icon"


    default_python_value = "0"
    default_prop_value = 0

    def get_python_repr(self):
        value = self.default_value
        return f"{value}"


    default_value: bpy.props.IntProperty(name="Value",
                                            description="Value of this socket",
                                            get=ScriptingSocket._get_value,
                                            set=ScriptingSocket._set_value)

    named_icon: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="FILE_PATH",
                                            update=ScriptingSocket._update_value)


    subtypes = ["NONE", "STRING_VALUE"]
    subtype_values = {"NONE": "default_value", "NAMED_ICON": "named_icon"}


    def get_color(self, context, node):
        return (1,0.4,0.2)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
        if not self.is_linked and not self.is_output:
            row = layout.row()
            row.scale_x = 1.74
            op = row.operator("sn.select_icon", text="Choose Icon", icon_value=self.default_value)
            op.node = node.name
            op.socket = self.index

