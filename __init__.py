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
    "name" : "Visual Scripting",
    "author" : "Joshua Knauber, Finn Knauber",
    "description" : "Adds a new node editor for writing scripts and addons with nodes",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0),
    "location" : "Editors -> Scripting Nodes",
    "warning" : "",
    "category" : "Node"
}

import bpy
from . import auto_load
from .node_categories import get_node_categories
from .interface import node_tree_header
import nodeitems_utils

auto_load.init()

@bpy.app.handlers.persistent
def load_post(scene):
    from .properties.property_utils import add_error_prop, clear_error_props
    clear_error_props()
    add_error_prop("BAD ERROR","test message for this errors message",True,"")
    add_error_prop("BAD ERROR","test message for this errors message",True,"Panel")

def register():
    auto_load.register()
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())
    bpy.types.NODE_HT_header.append(node_tree_header)
    bpy.app.handlers.load_post.append(load_post)

def unregister():
    auto_load.unregister()
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')
    bpy.types.NODE_HT_header.remove(node_tree_header)
