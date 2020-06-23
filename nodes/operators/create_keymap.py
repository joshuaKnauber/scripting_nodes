"""import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_KeyItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Key type",description="Type of the key")

class SN_KeymapItem(bpy.types.PropertyGroup):

    def get_value_items(self, context):
        values = ["ANY", "PRESS", "RELEASE", "CLICK", "DOUBLE_CLICK", "CLICK_DRAG", "NORTH", "NORTH_EAST", "EAST", "SOUTH_EAST", "SOUTH", "SOUTH_WEST", "WEST", "NORTH_WEST", "NOTHING"]
        items = []
        for item in values:
            items.append((item,item.replace("_"," ").title(),item.replace("_"," ").title()))
        return items

    def get_key_items(self,context):
        types = ["NONE", "LEFTMOUSE", "MIDDLEMOUSE", "RIGHTMOUSE", "BUTTON4MOUSE", "BUTTON5MOUSE", "BUTTON6MOUSE", "BUTTON7MOUSE", "PEN", "ERASER", "MOUSEMOVE", "INBETWEEN_MOUSEMOVE", "TRACKPADPAN", "TRACKPADZOOM", "MOUSEROTATE", "MOUSESMARTZOOM", "WHEELUPMOUSE", "WHEELDOWNMOUSE", "WHEELINMOUSE", "WHEELOUTMOUSE"]
        items = []
        for item in types:
            items.append((item,item.replace("_"," ").title(),item.replace("_"," ").title()))
        return items

    alt: bpy.props.BoolProperty(name="Alt",description="Alt button needs to be pressed")
    ctrl: bpy.props.BoolProperty(name="Ctrl",description="Ctrl button needs to be pressed")
    shift: bpy.props.BoolProperty(name="Shift",description="Shift button needs to be pressed")
    any_modifier: bpy.props.BoolProperty(name="Any modifier key",description="Alt, Ctrl or shift needs to be pressed")
    value: bpy.props.EnumProperty(name="Value",description="Value of the shortcut",items=get_value_items)

    use_mouse: bpy.props.BoolProperty(name="Mouse shortcut",description="Use a mouse shortcut",default=False)
    key_type: bpy.props.EnumProperty(name="Key type",description="Type of the key",items=get_key_items)
    key_name: bpy.props.StringProperty(name="Key type",description="Type of the key")


bpy.utils.register_class(SN_KeymapItem)


class SN_CreateKeymap(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateKeymap"
    bl_label = "Create Keymap"
    bl_icon = node_icons["OPERATOR"]
    _should_be_registered = True
    bl_width_default = 200

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def mode_items(self,context):
        modes = ["EDIT_MESH", "EDIT_CURVE", "EDIT_SURFACE", "EDIT_TEXT", "EDIT_ARMATURE", "EDIT_METABALL", "EDIT_LATTICE", "POSE", "SCULPT", "PAINT_WEIGHT", "PAINT_VERTEX", "PAINT_TEXTURE", "PARTICLE", "OBJECT", "PAINT_GPENCIL", "EDIT_GPENCIL", "SCULPT_GPENCIL", "WEIGHT_GPENCIL", "VERTEX_GPENCIL"]
        items = []
        for mode in modes:
            items.append((mode,mode.replace("_", " ").title(),mode.replace("_", " ").title()))
        return items

    mode: bpy.props.EnumProperty(name="Mode",description="The mode the keymap should work in",items=mode_items,update=socket_update)

    def space_items(self,context):
        return [("EMPTY","All Spaces","All spaces")] + self.UiLocationHandler.space_type_items()

    space_type: bpy.props.EnumProperty(name="Space",description="Space the keymap should work in",items=space_items,update=socket_update)

    keymap_items: bpy.props.CollectionProperty(type=SN_KeymapItem)

    key_items: bpy.props.CollectionProperty(type=SN_KeyItem)

    def load_keys(self):
        types = [ "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "LEFT_CTRL", "LEFT_ALT", "LEFT_SHIFT", "RIGHT_ALT", "RIGHT_CTRL", "RIGHT_SHIFT", "OSKEY", "APP", "GRLESS", "ESC", "TAB", "RET", "SPACE", "LINE_FEED", "BACK_SPACE", "DEL", "SEMI_COLON", "PERIOD", "COMMA", "QUOTE", "ACCENT_GRAVE", "MINUS", "PLUS", "SLASH", "BACK_SLASH", "EQUAL", "LEFT_BRACKET", "RIGHT_BRACKET", "LEFT_ARROW", "DOWN_ARROW", "RIGHT_ARROW", "UP_ARROW", "NUMPAD_2", "NUMPAD_4", "NUMPAD_6", "NUMPAD_8", "NUMPAD_1", "NUMPAD_3", "NUMPAD_5", "NUMPAD_7", "NUMPAD_9", "NUMPAD_PERIOD", "NUMPAD_SLASH", "NUMPAD_ASTERIX", "NUMPAD_0", "NUMPAD_MINUS", "NUMPAD_ENTER", "NUMPAD_PLUS", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24", "PAUSE", "INSERT", "HOME", "PAGE_UP", "PAGE_DOWN", "END", "MEDIA_PLAY", "MEDIA_STOP", "MEDIA_FIRST", "MEDIA_LAST"]
        for key in types:
            item = self.key_items.add()
            item.name = key

    def init(self, context):
        self.load_keys()
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

    def draw_buttons(self, context, layout):
        layout.prop(self,"mode",text="Mode")
        layout.prop(self,"space_type",text="Space")
        layout.separator()

        row = layout.row()
        row.scale_y = 1.25
        row.operator("scripting_nodes.add_keymap_item",icon="ADD",text="Add shortcut").node_name = self.name
        for index, item in enumerate(self.keymap_items):
            box = layout.box()
            row = box.row()
            op = row.operator("scripting_nodes.remove_keymap_item",icon="PANEL_CLOSE",text="",emboss=False)

            col = box.column(align=True)

            col.prop(item,"use_mouse")
            
            if not item.use_mouse:
                col.prop_search(item,"key_name", self, "key_items",text="")
            else:
                col.prop(item,"key_type",text="")

            col.prop(item,"value",text="")

            col.prop(item,"any_modifier",toggle=True)
            col.prop(item,"ctrl",toggle=True)
            col.prop(item,"alt",toggle=True)
            col.prop(item,"shift",toggle=True)

            op.node_name = self.name
            op.index = index

        if not len(self.keymap_items):
            layout.label(text="No shortcuts added")

    def evaluate(self, output):
        return {"blocks": [],"errors": []}

    def needed_imports(self):
        return ["bpy"]

    def get_register_block(self):
        keys = []
        for item in self.keymap_items:
            key = []
        return ["km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=\""+self.mode+"\", space_type=\""+self.space_type+"\")"] + keys + ["addon_keymaps.append(km)"]

    def get_unregister_block(self):
        return [
            "for km in addon_keymaps:",
            "    bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)",
            "addon_keymaps.clear()"
        ]"""