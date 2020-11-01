#SN_PopoverNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from uuid import uuid4


class SN_PopoverNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PopoverNode"
    bl_label = "Popover"
    bl_icon = "DOWNARROW_HLT"
    node_color = (0.89,0.6,0)
    bl_width_default = 200
    should_be_registered = False

    docs = {
        "text": ["The popover node displays a <important>popover from a selected panel</>.",
                "",],
        "python": ["layout.<function>popover</>(<string>\"SN_PT_MyPanel\"</>)"]
    }

    def update_custom(self,context):
        self.panelProp = ""
        self.panel_name = ""

    panelProp: bpy.props.StringProperty()
    panel_name: bpy.props.StringProperty()
    use_custom: bpy.props.EnumProperty(items=[("CUSTOM","Custom","Custom"),("INTERNAL","Internal","Internal")], update=update_custom,
                                        name="Use Custom", description="Use your own items or blenders internals")

    popover_uid: bpy.props.StringProperty()

    def inititialize(self,context):
        self.popover_uid = uuid4().hex[:10]
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"STRING","Text")

    def copy(self,context):
        self.popover_uid = uuid4().hex[:10]

    def draw_buttons(self,context,layout):
        self.draw_icon_chooser(layout)
        # layout.prop(self,"use_custom",expand=True,text=" ")

        if self.use_custom == "CUSTOM":
            layout.prop_search(self,"panelProp",bpy.context.space_data.node_tree,"sn_panel_collection_property",text="")
        else:
            layout.label(text="Some panels only work in certain spaces!")
            txt = "Select location"
            if self.panelProp:
                txt = self.panel_name
            op = layout.operator("visual_scripting.create_existing_panel_location",icon="EYEDROPPER",text=txt)
            op.panel_uid = self.popover_uid
            op.shortcut_index = 0

    def evaluate(self, socket, node_data, errors):
        layout_type = self.inputs[0].links[0].from_node.layout_type()
        icon = self.icon
        if icon:
            icon = f", icon=\"{icon}\""
        
        popover = []

        panel_name = ""
        if self.use_custom == "CUSTOM":
            for panel in bpy.context.space_data.node_tree.sn_panel_collection_property:
                if panel.name == self.panelProp:
                    panel_name = "\"" + panel.identifier + "\""
        else:
            panel_name = self.panelProp
        
        if panel_name:
            popover = [layout_type, ".popover(", panel_name, ",text=", node_data["input_data"][1]["code"] , icon, ")"]
        else:
            errors.append({"title": "No valid panel selected!", "message": "Please select a valid panel to draw the popover", "node": self, "fatal": True})

        return {
            "blocks": [
                {
                    "lines": [
                        popover
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }

