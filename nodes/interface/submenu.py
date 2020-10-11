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
        "text": ["The node adds a <important>submenu</> to your interface.",
                "",
                "Internal/Custom: <subtext>Internal shows a list of the blender menus and custom shows the ones you create in your addon</>",
                "                           <subtext>You can select the menu from the search below this</>",
                "Layout: <subtext>The layout the menu will be shown in</>",
                "Text: <subtext>The text that will be shown on the input</>"],
        "python": ["layout.<function>menu</>(<string>\"VIEW3D_MT_transform\"</>)"]
    }

    def update_enum(self,context):
        self.menu_identifier = ""
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
        if self.menu_identifier:

            if self.search_prop == "CUSTOM":
                if self.menu_identifier in node_data["node_tree"].sn_menu_collection_property:
                    menu = [layout_type,".menu(\"",node_data["node_tree"].sn_menu_collection_property[self.menu_identifier].identifier,"\",text=",node_data["input_data"][1]["code"],icon,")"]

            else:
                menu = [layout_type,".menu(\"",self.menu_options[self.menu_identifier].identifier,"\",text=",node_data["input_data"][1]["code"],icon,")"]

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

