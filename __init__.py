# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os

import bpy
from bpy.utils import previews

from . import auto_load, handlers
from .addon.addon_properties import SNA_AddonProperties
from .interface.header.header import (
    group_interface_append,
    header_append,
    header_prepend,
)
from .interface.menus.add_menu.node_categories import (
    draw_node_menu,
    register_node_menus,
    unregister_node_menus,
)
from .interface.menus.rightclick import serpens_right_click
from .keymaps.keymap import register_keymaps, unregister_keymaps
from .msgbus import subscribe_to_name_change, unsubscribe_from_name_change

bl_info = {
    "name": "Serpens - Scripting Nodes",
    "author": "Joshua Knauber, Finn Knauber",
    "description": "Adds a node editor for building addons with nodes",
    "blender": (4, 0, 0),
    "version": (4, 0, 0),
    "location": "Editors -> Scripting Node Editor",
    "doc_url": "https://joshuaknauber.notion.site/Serpens-Documentation-d44c98df6af64d7c9a7925020af11233",
    "tracker_url": "https://discord.com/invite/NK6kyae",
    "category": "Node",
}


auto_load.init()


def register_icons():
    bpy.types.Scene.sna_icons = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")

    icons = ["discord", "serpens"]

    for icon in icons:
        bpy.types.Scene.sna_icons.load(
            icon, os.path.join(icons_dir, icon + ".png"), "IMAGE"
        )


def unregister_icons():
    bpy.utils.previews.remove(bpy.types.Scene.sna_icons)


def register():
    # register the classes of the addon
    auto_load.register()

    # addon properties
    bpy.types.Scene.sna = bpy.props.PointerProperty(
        type=SNA_AddonProperties, name="Serpens Properties"
    )

    # msgbus
    subscribe_to_name_change()

    # register the keymaps
    register_keymaps()

    # register the icons
    register_icons()

    # register node categories
    register_node_menus()
    bpy.types.NODE_MT_add.append(draw_node_menu)

    # add the headers
    bpy.types.NODE_HT_header.append(header_append)
    bpy.types.NODE_MT_editor_menus.append(header_prepend)
    bpy.types.NODE_PT_node_tree_interface.append(group_interface_append)

    # app handlers
    handlers.register()

    # add right click menu
    bpy.types.WM_MT_button_context.append(serpens_right_click)


def unregister():
    # remove the headers
    bpy.types.NODE_MT_editor_menus.remove(header_prepend)
    bpy.types.NODE_HT_header.remove(header_append)
    bpy.types.NODE_PT_node_tree_interface.remove(group_interface_append)

    # addon properties
    del bpy.types.Scene.sna

    # msgbus
    unsubscribe_from_name_change()

    # unregister the keymaps
    unregister_keymaps()

    # unregister the icons
    unregister_icons()

    # unregister node categories
    bpy.types.NODE_MT_add.remove(draw_node_menu)
    unregister_node_menus()

    # remove handlers
    handlers.unregister()

    # remove right click menu
    if hasattr(bpy.types, "WM_MT_button_context"):
        bpy.types.WM_MT_button_context.remove(serpens_right_click)

    # unregister the addon classes
    auto_load.unregister()
