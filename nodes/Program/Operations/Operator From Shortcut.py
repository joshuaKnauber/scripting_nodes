import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ShortcutOperatorOption(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    operator: bpy.props.StringProperty()
    settings: bpy.props.StringProperty()
    
    
    
class SN_OT_ShortcutToNode(bpy.types.Operator):
    bl_idname = "sn.shortcut_to_node"
    bl_label = "Shortcut To Node"
    bl_description = "Add a node with the operator from this shortcut pasted in"
    bl_options = {"REGISTER", "INTERNAL"}

    operator: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    settings: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    button: bpy.props.BoolProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        if self.button:
            bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_ButtonNodeNew", use_transform=True)
        else:
            bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_RunOperatorNode", use_transform=True)
        node = context.space_data.node_tree.nodes.active
        node.pasted_operator = self.operator
        if self.settings:
            settings = self.settings.split("|")
            for setting in settings:
                name = setting.split("&&")[0].replace("_", " ").title()
                value = setting.split("&&")[1]
                if name in node.inputs:
                    node.inputs[name].disabled = False
                    node.inputs[name].default_value = value
        return {"FINISHED"}




class SN_FindShortcutOperator(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_FindShortcutOperator"
    bl_label = "Find Operator From Shortcut"
    bl_width_default = 240

    options: bpy.props.CollectionProperty(type=SN_ShortcutOperatorOption)
    selected: bpy.props.StringProperty()
    
    def update_shortcut(self, context):
        options = self.find_operators_for_key()
        self.options.clear()
        for option in options:
            item = self.options.add()
            item.name = option[0]
            item.operator = option[1]
            item.settings = option[2]
    
    key: bpy.props.StringProperty(name="Key", default="A", update=update_shortcut)

    recording: bpy.props.BoolProperty(name="Recording", default=False)
    
    shift: bpy.props.BoolProperty(name="Shift", default=True, update=update_shortcut)
    ctrl: bpy.props.BoolProperty(name="Ctrl", default=False, update=update_shortcut)
    alt: bpy.props.BoolProperty(name="Alt", default=False, update=update_shortcut)
    oskey: bpy.props.BoolProperty(name="OS Key", default=False, update=update_shortcut)

    def on_create(self, context):
        self.update_shortcut(context)
    
    def draw_node(self, context, layout):
        layout.operator("sn.record_key", text=self.key, depress=self.recording).node = self.name
        row = layout.row(align=True)
        row.prop(self, "shift", toggle=True)
        row.prop(self, "ctrl", toggle=True)
        row.prop(self, "alt", toggle=True)
        row.prop(self, "oskey", toggle=True)
        layout.prop_search(self, "selected", self, "options", text="")
        row = layout.row(align=True)
        row.enabled = self.selected in self.options
        row.scale_y = 1.2
        op = row.operator("sn.shortcut_to_node", text="Run Operator", icon="POSE_HLT")
        op.button = False
        op.operator = "" if not self.selected in self.options else self.options[self.selected].operator
        op.settings = "" if not self.selected in self.options else self.options[self.selected].settings
        op = row.operator("sn.shortcut_to_node", text="Button", icon="MOUSE_LMB")
        op.button = True
        op.operator = "" if not self.selected in self.options else self.options[self.selected].operator
        op.settings = "" if not self.selected in self.options else self.options[self.selected].settings

    def find_operators_for_key(self):
        options = []
        for keymap in bpy.context.window_manager.keyconfigs.user.keymaps:
            for item in keymap.keymap_items:
                if item.type == self.key and item.shift == self.shift and item.ctrl == self.ctrl \
                    and item.alt == self.alt and item.oskey == self.oskey:
                    if item.idname:
                        props = ""
                        prop_str = ""
                        settings = ""
                        if item.properties:
                            for prop in item.properties.keys():
                                if type(item.properties[prop]) == str:
                                    props += f"{prop}='{item.properties[prop]}', "
                                    prop_str += f"'{item.properties[prop]}', "
                                else:
                                    props += f"{prop}={item.properties[prop]}, "
                                    prop_str += f"{item.properties[prop]}, "
                                settings += f"{prop}&&{item.properties[prop]}|"
                        name = item.name if item.name else item.idname.replace("_", " ").title()
                        area = keymap.space_type.replace("_", " ").title() if keymap.space_type != "EMPTY" else "Any"
                        if prop_str:
                            prop_str = f" [{prop_str[:-2]}]"
                            settings = settings[:-1]
                        op = f"bpy.ops.{item.idname}('INVOKE_DEFAULT', {props})"
                        options.append((f"{name} ({area}){prop_str}", op, settings))
        return options