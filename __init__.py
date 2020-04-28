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
    "wiki_url": "",
    "warning" : "",
    "category" : "Node"
}

import bpy
from . import auto_load
from .node_categories import get_node_categories
from .interface import node_tree_header
import nodeitems_utils

auto_load.init()

def register():
    auto_load.register()
    nodeitems_utils.register_node_categories('SCRIPTING_NODES', get_node_categories())
    bpy.types.NODE_HT_header.append(node_tree_header)

def unregister():
    auto_load.unregister()
    nodeitems_utils.unregister_node_categories('SCRIPTING_NODES')
    bpy.types.NODE_HT_header.remove(node_tree_header)
