import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_CreateKeymap(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateKeymap"
    bl_label = "Create Keymap"
    bl_icon = node_icons["OPERATOR"]
    _should_be_registered = True

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

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

    def draw_buttons(self, context, layout):
        layout.label(text="Mode:")
        layout.prop(self,"mode",text="")
        layout.label(text="Space:")
        layout.prop(self,"space_type",text="")

    def evaluate(self, output):
        error_list = []

        return {
            "blocks": [
                {
                    "lines": [
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": error_list
        }

    def needed_imports(self):
        return ["bpy"]

    def get_register_block(self):
        keys = []
        return ["km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name=\""+self.mode+"\", space_type=\""+self.space_type+"\")"] + keys + ["addon_keymaps.append(km)"]

    def get_unregister_block(self):
        return [
            "for km in addon_keymaps:",
            "    bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)",
            "addon_keymaps.clear()"
        ]