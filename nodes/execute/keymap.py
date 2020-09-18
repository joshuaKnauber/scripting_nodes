#SN_KeymapNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python
from ...operators.panel_ops import get_possible_panel_locations
from uuid import uuid4


class SN_RecordShortcut(bpy.types.Operator):
    bl_idname = "scripting_nodes.record_shortcut"
    bl_label = "Record Shortcut"
    bl_description = "Records the next shortcut after pressing this button"
    bl_options = {'REGISTER',"UNDO","INTERNAL"}

    node_name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        context.scene.sn_properties.recording_shortcut = True
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        
        if event.type and not event.type in ["MOUSEMOVE", "INBETWEEN_MOUSEMOVE"]:
            context.scene.sn_properties.recording_shortcut = False
            shortcut = context.space_data.node_tree.nodes[self.node_name].shortcuts[self.index]
            shortcut.event_type = event.type
            context.area.tag_redraw()
            return {"FINISHED"}
        
        return {"RUNNING_MODAL"}


class SN_OT_RemoveKey(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_key"
    bl_label = "Remove Key"
    bl_description = "Removes the shortcut type"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    node_name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].shortcuts[self.index].event_type = "NONE"
        return {"FINISHED"}


class SN_OT_RemoveShortcut(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_shortcut"
    bl_label = "Remove Shortcut"
    bl_description = "Removes the shortcut"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    node_name: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].shortcuts.remove(self.index)
        return {"FINISHED"}


class SN_ShortcutPropertyGroup(bpy.types.PropertyGroup):
    shift: bpy.props.BoolProperty(default=False,name="Shift",description="Use the Shift modifier key for this shortcut")
    ctrl: bpy.props.BoolProperty(default=False,name="Ctrl",description="Use the Ctrl modifier key for this shortcut")
    alt: bpy.props.BoolProperty(default=False,name="Alt",description="Use the Alt modifier key for this shortcut")
    any_mod: bpy.props.BoolProperty(default=False,name="Any Modifier",description="Use any modifier key for this shortcut")

    repeat: bpy.props.BoolProperty(default=False,name="Active on Key-Repeat", description="Active on key-repeat events (when a key is held)")
    value: bpy.props.EnumProperty(items=[("ANY","Any","Any"),("PRESS","Press","Press"),("RELEASE","Release","Release"),
                                ("CLICK","Click","Click"),("DOUBLE_CLICK","Double Click","Double Click")],
                                name="Value", description="The value of the shortcut", default="PRESS")

    event_type: bpy.props.StringProperty(default="NONE")

    call_type: bpy.props.EnumProperty(items=[("OPERATOR","Operator","Operator"),("PANEL","Panel","Panel"),("PIE_MENU"," Pie Menu","Pie Menu"),("MENU"," Menu","Menu")])
    custom_type: bpy.props.EnumProperty(items=[("CUSTOM","Custom","Custom"),("INTERNAL","Internal","Internal")])

    operator: bpy.props.StringProperty(name="Operator",description="The operator that will be run when the shortcut is executed")
    panel: bpy.props.StringProperty(name="Operator",description="The operator that will be run when the shortcut is executed")
    menu: bpy.props.StringProperty(name="Operator",description="The operator that will be run when the shortcut is executed")
    pie_menu: bpy.props.StringProperty(name="Operator",description="The operator that will be run when the shortcut is executed")


class SN_OT_AddShortcut(bpy.types.Operator):
    bl_idname = "scripting_nodes.add_shortcut"
    bl_label = "Add Shortcut"
    bl_description = "Adds a shortcut to this node"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node_name]
        node.shortcuts.add()
        return {"FINISHED"}



class SN_KeymapNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_KeymapNode"
    bl_label = "Keymap"
    bl_icon = "FILE_SCRIPT"
    bl_width_default = 250
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = True

    docs = {
        "text": ["This node is used to <important>run a script</>.",
                "",
                "<important>Make sure your script doesn't have functions and works before selecting it here</>"],
        "python": []

    }

    def get_space_items(self,context):
        spaces = []
        for item in get_possible_panel_locations():
            if not item["space"] in spaces:
                spaces.append(item["space"])
        
        items = []
        for space in spaces:
            items.append((space,space.replace("_"," ").title(),space.replace("_"," ").title()))
        return items

    keymap_uid: bpy.props.StringProperty()
    shortcuts: bpy.props.CollectionProperty(type=SN_ShortcutPropertyGroup)
    space_type: bpy.props.EnumProperty(name="Space",items=get_space_items)

    def inititialize(self, context):
        self.keymap_uid = uuid4().hex[:10]

    def copy(self,context):
        self.keymap_uid = uuid4().hex[:10]

    def draw_buttons(self,context,layout):
        layout.prop(self,"space_type",text="")
        layout.operator("scripting_nodes.add_shortcut",icon="ADD").node_name = self.name

        for index, shortcut in enumerate(self.shortcuts):

            col = layout.column(align=True)

            box = col.box()

            row = box.row()
            row.label(text=shortcut.call_type.replace("_"," ").title() + " Shortcut")
            op = row.operator("scripting_nodes.remove_shortcut",text="",icon="PANEL_CLOSE",emboss=False)
            op.node_name = self.name
            op.index = index

            _col = box.column(align=True)
            row = _col.row()
            row.prop(shortcut,"call_type",text=" ",expand=True)
            row = _col.row()
            row.prop(shortcut,"custom_type",text=" ",expand=True)

            if shortcut.call_type == "OPERATOR":
                if shortcut.custom_type == "INTERNAL":
                    pass
                else:
                    box.prop_search(shortcut,"operator",bpy.context.space_data.node_tree,"custom_operator_properties",text="")

            elif shortcut.call_type == "PANEL":
                if shortcut.custom_type == "INTERNAL":
                    pass
                else:
                    box.prop_search(shortcut,"panel",bpy.context.space_data.node_tree,"sn_panel_collection_property",text="")

            elif shortcut.call_type == "PIE_MENU":
                if shortcut.custom_type == "INTERNAL":
                    pass
                else:
                    box.prop_search(shortcut,"pie_menu",bpy.context.space_data.node_tree,"sn_pie_menu_collection_property",text="")

            elif shortcut.call_type == "MENU":
                if shortcut.custom_type == "INTERNAL":
                    pass
                else:
                    box.prop_search(shortcut,"menu",bpy.context.space_data.node_tree,"sn_menu_collection_property",text="")


            box = col.box()

            row = box.row(align=True)

            row.prop(shortcut,"any_mod",text="",toggle=True,icon="MODIFIER_DATA")
            _row = row.row(align=True)
            _row.enabled = not shortcut.any_mod
            _row.prop(shortcut,"shift",text="",toggle=True,icon="EVENT_SHIFT")
            _row.prop(shortcut,"ctrl",text="",toggle=True,icon="EVENT_CTRL")
            _row.prop(shortcut,"alt",text="",toggle=True,icon="EVENT_ALT")
            
            if not context.scene.sn_properties.recording_shortcut:
                op = row.operator("scripting_nodes.record_shortcut",text=shortcut.event_type.replace("_", " ").title())
                op.node_name = self.name
                op.index = index

                if shortcut.event_type != "NONE":
                    op = row.operator("scripting_nodes.remove_key",text="",icon="REMOVE")
                    op.node_name = self.name
                    op.index = index
            else:
                row.label(text="Awaiting input...")

            row = box.row(align=True)
            row.prop(shortcut,"value",text="")
            row.prop(shortcut,"repeat",text="Repeat Key",icon="LOOP_BACK")

        if len(self.shortcuts) == 0:
            layout.label(text="No shortcuts added")

    def function_name(self):
        return "register_keymap_"+self.keymap_uid

    def get_register_block(self):
        return [self.function_name()+"()"]

    def get_unregister_block(self):
        return []

    def evaluate(self, socket, node_data, errors):
        shortcuts = []

        for item in self.shortcuts:
            shortcut = []

            if item.call_type == "OPERATOR":
                pass
        
            elif item.call_type == "PANEL":
                pass

            elif item.call_type == "PIE_MENU":
                idname = "wm.call_menu_pie"

            elif item.call_type == "MENU":
                pass

            shortcut.append([ f"kmi = km.keymap_items.new(idname=\"{idname}\",type=\"{item.event_type}\",value=\"{item.value}\",shift={str(item.shift)},ctrl={str(item.ctrl)},alt={str(item.alt)},repeat={str(item.repeat)})" ])
            
            if item.call_type == "PIE_MENU":
                if item.custom_type == "CUSTOM":
                    shortcut.append([ "kmi.properties.name = \"", node_data["node_tree"].sn_pie_menu_collection_property[item.pie_menu].identifier, "\"" ])
                else:
                    pass

            shortcut.append(["addon_keymaps.append((km, kmi))"])

            shortcuts += shortcut

        return {"blocks": [
            {
                "lines": [
                    ["def ",self.function_name(),"():"],
                ],
                "indented": [
                    ["global addon_keymaps"],
                    ["kc = bpy.context.window_manager.keyconfigs.addon"],
                    [""],
                    ["km = kc.keymaps.new(name=\"",self.space_type.replace("_"," ").title(),"\", space_type=\"",self.space_type,"\")"],
                    [""]
                ]+shortcuts+[[""]]
            }
        ],"errors": errors}
