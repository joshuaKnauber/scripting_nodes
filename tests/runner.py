"""Test entry point executed *inside* Blender (see scripts/test.py).

Enables the addon from the temp `user_default` repo, discovers every
`tests/test_*.py` module and runs it with unittest. Exits with a non-zero code
on failure so CI can pick it up.
"""

import os
import sys
import traceback
import unittest

# Blender ignores PYTHONUNBUFFERED; without this, output is lost if Blender crashes
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TESTS_DIR)


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    pattern = ""
    verbose = "--verbose" in argv
    if "--pattern" in argv:
        i = argv.index("--pattern")
        if i + 1 < len(argv):
            pattern = argv[i + 1]
    return pattern, verbose


def iter_tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from iter_tests(item)
        else:
            yield item


def main():
    import helpers

    try:
        helpers.enable_addon()
    except Exception:
        traceback.print_exc()
        print("FAILED: addon could not be enabled")
        sys.exit(1)

    pattern, verbose = parse_args()
    loader = unittest.TestLoader()
    suite = loader.discover(TESTS_DIR, pattern="test_*.py", top_level_dir=TESTS_DIR)
    if pattern:
        suite = unittest.TestSuite(t for t in iter_tests(suite) if pattern in t.id())

    result = unittest.TextTestRunner(verbosity=2 if verbose else 1).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


main()
