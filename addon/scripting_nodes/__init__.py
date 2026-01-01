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

# Create module alias for extension compatibility
# Extensions are loaded as bl_ext.<repo>.<name>, but imports use 'scripting_nodes'
import sys
from pathlib import Path

sys.modules["scripting_nodes"] = sys.modules[__name__]

# Load bundled wheels (needed for dev workflow; installed extensions load these automatically)
_wheels_dir = Path(__file__).parent / "wheels"
if _wheels_dir.exists():
    for whl in _wheels_dir.glob("*.whl"):
        whl_path = str(whl)
        if whl_path not in sys.path:
            sys.path.insert(0, whl_path)

bl_info = {
    "name": "Scripting Nodes",
    "author": "Joshua Knauber, Finn Knauber",
    "description": "Adds a node editor for building addons with nodes",
    "blender": (4, 3, 0),
    "version": (4, 0, 0),
    "location": "Editors -> Visual Scripting Editor",
    "category": "Node",
}

import bpy
from . import auto_load


auto_load.init()


def register():
    auto_load.register()


def unregister():
    auto_load.unregister()
