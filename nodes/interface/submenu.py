#SN_SubMenuNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_MenusPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="")
    identifier: bpy.props.StringProperty(default="")

class SN_SubMenuNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SubMenuNode"
    bl_label = "Submenu"
    bl_icon = "DOWNARROW_HLT"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    docs = {
        "text": ["The row node can display a layout in <important> a row or from left to right</>.",
                "",
                "Aligned: <subtext>All following nodes are aligned</>",
                "Enabled: <subtext>Only displays a column if this is True</>",
                "Alert: <subtext>Is diplayed red like an alert</>"],
        "python": ["layout.<function>row</>(align=True)"]
    }

    def update_enum(self,context):
        if self.search_prop == "INTERNAL":
            self.menu_options.clear()
            for menu_name in dir(bpy.types):
                if "_MT_" in menu_name:
                    menu = eval("bpy.types."+menu_name)
                    item = self.menu_options.add()
                    item.name = menu_name
                    if hasattr(menu,"bl_label") and menu.bl_label and not menu.bl_label in self.menu_options:
                        item.name = menu.bl_label
                    item.identifier = menu_name

    menu_identifier: bpy.props.StringProperty()
    menu_options: bpy.props.CollectionProperty(type=SN_MenusPropertyGroup)
    search_prop: bpy.props.EnumProperty(items=[("INTERNAL", "Internal", "Blenders internal properties"), ("CUSTOM", "Custom", "Your custom enums")], name="Properties", description="Which properties to display", update=update_enum)

    def inititialize(self,context):
        self.search_prop = "CUSTOM"
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"STRING","Text")

    def draw_buttons(self,context,layout):
        self.draw_icon_chooser(layout)
        layout.prop(self,"search_prop",text=" ",expand=True)

        if self.search_prop == "INTERNAL":
            layout.prop_search(self,"menu_identifier",self,"menu_options",text="")
        else:
            layout.prop_search(self,"menu_identifier",context.space_data.node_tree,"sn_menu_collection_property",text="")

    def evaluate(self, socket, node_data, errors):
        layout_type = self.inputs[0].links[0].from_node.layout_type()

        icon = ""
        if self.icon:
            icon = ",icon=\""+self.icon+"\""

        menu = []
        name = self.menu_identifier
        if name:
            self.search_prop = self.search_prop
            for prop in self.menu_options:
                if prop.name == name:
                    menu = [layout_type,".menu(\"",prop.identifier,"\",text=",node_data["input_data"][1]["code"],icon,")"]

        return {
            "blocks": [
                {
                    "lines": [
                        menu
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }
    
    def layout_type(self):
        return "row"

