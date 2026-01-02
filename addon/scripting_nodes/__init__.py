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

import sys
import os
from pathlib import Path


def _is_extension():
    """Check if running as a Blender extension (bl_ext.*)."""
    return __name__.startswith("bl_ext.")


def _wheels_available():
    """Check if wheel packages are already available."""
    try:
        import names_generator

        return True
    except ImportError:
        return False


# Wheel loading strategy:
# 1. When running as extension AND wheels are available: Blender loaded them, do nothing
# 2. When running as extension but wheels missing: dev workflow issue, load manually
# 3. When not running as extension: legacy addon mode, load manually
#
# We only avoid sys.path modification when Blender has properly loaded the wheels,
# which is the case for proper extension installations from the repository.
if not _wheels_available():
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
