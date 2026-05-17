from ....lib.utils.screen.screen import redraw_all
from ....lib.utils.logger import fmt_duration, log_if
from .modules.modules import (
    reload_addon,
    reload_tree_module,
    unregister_module,
)
from ....lib.utils.node_tree.scripting_node_trees import (
    has_addon,
    scripting_node_trees,
)
from .dependencies import get_dependent_trees
from .generator import generate_addon, has_changes
import sys
import time
import bpy


def _expand_with_dependents(changed_modules):
    """Add transitive dependent trees to the reload set."""
    result = set(changed_modules)
    name_to_ntree = {n.module_name: n for n in scripting_node_trees()}
    for module_name in changed_modules:
        ntree = name_to_ntree.get(module_name)
        if ntree:
            result.update(get_dependent_trees(ntree))
    return result


def watch_changes():
    module_name = bpy.context.scene.sna.addon.module_name

    if has_changes() and has_addon():
        if bpy.context.scene.sna.addon.enabled:
            log_reloads = bpy.context.scene.sna.dev.log_reload_times
            t_gen = time.perf_counter()
            changed_trees, needs_full_reload = generate_addon()
            gen_time = time.perf_counter() - t_gen
            addon_loaded = module_name in sys.modules

            if needs_full_reload or not addon_loaded:
                t_reload = time.perf_counter()
                reload_addon(module_name)
                reload_time = time.perf_counter() - t_reload
                log_if(
                    log_reloads,
                    "INFO",
                    f"full reload [{module_name}]: codegen "
                    f"{fmt_duration(gen_time)}, reload "
                    f"{fmt_duration(reload_time)}",
                )
            elif changed_trees:
                to_reload = _expand_with_dependents(changed_trees)
                dep_count = len(to_reload) - len(changed_trees)
                t_reload = time.perf_counter()
                for tree_module in to_reload:
                    reload_tree_module(module_name, tree_module)
                reload_time = time.perf_counter() - t_reload
                if log_reloads:
                    direct = ", ".join(sorted(changed_trees))
                    dep_suffix = (
                        f" (+{dep_count} dep{'s' if dep_count != 1 else ''})"
                        if dep_count
                        else ""
                    )
                    log_if(
                        True,
                        "INFO",
                        f"smart reload [{direct}{dep_suffix}]: codegen "
                        f"{fmt_duration(gen_time)}, reload "
                        f"{fmt_duration(reload_time)}",
                    )
        else:
            unregister_module(module_name)
        redraw_all()

    if has_addon() or not bpy.context.scene.sna.addon.enabled:
        return 0.25
    return 1
