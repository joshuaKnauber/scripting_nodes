"""Script nodes calling functions of a text block, the generated panel and
the script (same as tests/visual/scenarios/script_node.py)."""

import importlib.util
import os

WINDOW_SIZE = (1600, 1000)
LAYOUT = "split"
SIDEBAR_TAB = "Object Tools"

_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "tests", "visual", "scenarios", "script_node.py",
)  # fmt: skip
_spec = importlib.util.spec_from_file_location("script_node", _path)
_scenario = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_scenario)

setup = _scenario.setup
after = _scenario.after
