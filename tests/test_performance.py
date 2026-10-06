"""Rough guard against the update pipeline becoming quadratic again."""

import time
import unittest

import bpy
import helpers

CHAIN = 300


class PerformanceTest(unittest.TestCase):
    def test_large_tree(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Perf Test"
        tree = helpers.new_tree("Big")
        prev = helpers.add_node(tree, "SNA_Node_Trigger").outputs[0]
        prints = []
        for i in range(CHAIN):
            p = helpers.add_node(tree, "SNA_Node_Print")
            p.inputs[1].value = f"line {i}"
            tree.links.new(prev, p.inputs[0])
            prev = p.outputs[0]
            prints.append(p)
        scheduler = helpers.sn("src.core.scheduler")

        scheduler.request_full()
        t0 = time.perf_counter()
        helpers.flush()
        full = time.perf_counter() - t0

        # edit at the end of the chain: only the chain up to the root rebuilds
        prints[-1].inputs[1].value = "changed"
        t0 = time.perf_counter()
        helpers.flush()
        incremental = time.perf_counter() - t0

        print(
            f"\n  {CHAIN + 1} nodes: full flush {full * 1000:.0f}ms, "
            f"edit {incremental * 1000:.0f}ms"
        )
        self.assertIn(repr("changed"), helpers.tree_source(tree))
        self.assertLess(full, 3)
        self.assertLess(incremental, 1)
        bpy.data.node_groups.remove(tree)
        scheduler.request_full()
        helpers.flush()
