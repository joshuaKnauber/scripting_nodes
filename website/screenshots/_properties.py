"""Loads the properties demo add-on (tests/visual/scenarios/_properties_demo.py)."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tests", "visual", "scenarios"))

from _properties_demo import build  # noqa: E402, F401
