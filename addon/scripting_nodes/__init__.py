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

# Version, name and Blender compatibility live in blender_manifest.toml.

import importlib.util
import sys
from pathlib import Path

# Blender installs the manifest wheels when the extension is installed from a
# zip. When the source folder is linked into a repo directly (dev / tests),
# they aren't installed, so put the bundled wheels on sys.path instead.
if importlib.util.find_spec("autopep8") is None:
    for whl in (Path(__file__).parent / "wheels").glob("*.whl"):
        if str(whl) not in sys.path:
            sys.path.insert(0, str(whl))

from . import auto_load  # noqa: E402


def register():
    # init() lives here (not at import time) so a disable -> enable cycle
    # imports fresh submodules instead of re-registering stale classes.
    auto_load.init()
    auto_load.register()


def unregister():
    auto_load.unregister()
    auto_load.purge_modules()
