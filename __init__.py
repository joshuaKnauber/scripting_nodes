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

bl_info = {
    "name": "Serpens",
    "author": "Joshua Knauber, Finn Knauber",
    "description": "Adds a node editor for building addons with nodes",
    "blender": (4, 2, 0),
    "version": (3, 4, 0),
    "location": "Editors -> Visual Scripting Editor",
    "doc_url": "https://joshuaknauber.notion.site/Serpens-Documentation-d44c98df6af64d7c9a7925020af11233",
    "tracker_url": "https://discord.com/invite/NK6kyae",
    "category": "Node",
}

import bpy
from bpy.utils import previews
import atexit

import os

from .keymaps.keymap import register_keymaps, unregister_keymaps
from .node_tree.node_categories import (
    draw_node_menu,
    register_node_menus,
    unregister_node_menus,
)
from .interface.header.header import (
    footer_status,
    header_prepend,
    header_append,
    node_info_append,
)
from .interface.panels.warnings import append_warning
from .interface.menus.rightclick import serpens_right_click
from .msgbus import subscribe_to_name_change, unsubscribe_from_name_change

from .settings.addon_properties import SN_AddonProperties

from . import handlers

from . import auto_load

auto_load.init()


def register_icons():
    bpy.types.Scene.sn_icons = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "assets", "icons")

    icons = ["discord", "serpens"]

    for icon in icons:
        bpy.types.Scene.sn_icons.load(
            icon, os.path.join(icons_dir, icon + ".png"), "IMAGE"
        )


def unregister_icons():
    bpy.utils.previews.remove(bpy.types.Scene.sn_icons)


def register():
    # register the classes of the addon
    auto_load.register()

    # addon properties
    bpy.types.Scene.sn = bpy.props.PointerProperty(
        type=SN_AddonProperties, name="Serpens Properties"
    )

    # register the keymaps
    register_keymaps()

    # register the icons
    register_icons()

    # register node categories
    register_node_menus()
    bpy.types.NODE_MT_add.append(draw_node_menu)

    # add the node tree header
    bpy.types.NODE_HT_header.append(header_append)
    bpy.types.NODE_MT_editor_menus.append(header_prepend)
    bpy.types.NODE_PT_active_node_generic.append(node_info_append)
    bpy.types.STATUSBAR_HT_header.append(footer_status)

    # add no edit warnings
    bpy.types.NODE_PT_node_tree_interface.append(append_warning)

    # add name change update
    subscribe_to_name_change()

    # app handlers
    bpy.app.handlers.depsgraph_update_post.append(handlers.depsgraph_handler)
    bpy.app.handlers.load_post.append(handlers.load_handler)
    bpy.app.handlers.load_pre.append(handlers.unload_handler)
    bpy.app.handlers.undo_post.append(handlers.undo_post)
    bpy.app.handlers.save_pre.append(handlers.save_pre)
    atexit.register(handlers.unload_handler)

    # add right click menu
    bpy.types.WM_MT_button_context.append(serpens_right_click)


def unregister():
    # remove the node tree header
    bpy.types.NODE_MT_editor_menus.remove(header_prepend)
    bpy.types.NODE_HT_header.remove(header_append)
    bpy.types.NODE_PT_active_node_generic.remove(node_info_append)
    bpy.types.STATUSBAR_HT_header.remove(footer_status)

    # remove no edit warnings
    bpy.types.NODE_PT_node_tree_interface.remove(append_warning)

    # addon properties
    del bpy.types.Scene.sn

    # unregister the keymaps
    unregister_keymaps()

    # unregister the icons
    unregister_icons()

    # unregister node categories
    bpy.types.NODE_MT_add.remove(draw_node_menu)
    unregister_node_menus()

    # remove handlers
    bpy.app.handlers.depsgraph_update_post.remove(handlers.depsgraph_handler)
    bpy.app.handlers.load_post.remove(handlers.load_handler)
    bpy.app.handlers.load_pre.remove(handlers.unload_handler)
    bpy.app.handlers.undo_post.remove(handlers.undo_post)
    bpy.app.handlers.save_pre.remove(handlers.save_pre)
    atexit.unregister(handlers.unload_handler)

    # remove name change msgbus
    unsubscribe_from_name_change()

    # remove right click menu
    if hasattr(bpy.types, "WM_MT_button_context"):
        bpy.types.WM_MT_button_context.remove(serpens_right_click)

    # unregister the addon classes
    auto_load.unregister()
